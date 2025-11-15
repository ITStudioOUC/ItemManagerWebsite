import csv
import io
from datetime import datetime, date, timedelta
from decimal import Decimal
import os

from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from openpyxl import load_workbook

from finance.models import Department
from personnel.models import Personnel

from .filters import EvaluationRecordFilter
from .models import EvaluationRecord
from .serializers import EvaluationRecordSerializer


class EvaluationRecordViewSet(viewsets.ModelViewSet):
    """考评记录视图集"""
    authentication_classes = [JWTAuthentication]
    queryset = EvaluationRecord.objects.select_related('department', 'personnel').all()
    serializer_class = EvaluationRecordSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EvaluationRecordFilter
    search_fields = ['item_description', 'remarks', 'personnel__name', 'department__name']
    ordering_fields = ['evaluation_date', 'created_at', 'total_score', 'bonus_score', 'deduction_score']
    ordering = ['-evaluation_date', '-created_at']

    @action(detail=False, methods=['get'], url_path='export')
    def export_records(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            return Response({'detail': '暂无数据可导出'}, status=status.HTTP_400_BAD_REQUEST)

        filename = f'evaluation_records_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write('\ufeff')

        writer = csv.writer(response)
        headers = [
            'id',
            'department_id',
            'department_name',
            'personnel_id',
            'personnel_name',
            'item_description',
            'bonus_score',
            'deduction_score',
            'total_score',
            'evaluation_date',
            'remarks',
            'created_at',
            'updated_at',
        ]
        writer.writerow(headers)

        for record in queryset:
            writer.writerow([
                record.id,
                record.department_id,
                record.department.name if record.department else '',
                record.personnel_id,
                record.personnel.name if record.personnel else '',
                record.item_description,
                f'{record.bonus_score:.2f}',
                f'{record.deduction_score:.2f}',
                f'{record.total_score:.2f}',
                record.evaluation_date.isoformat() if record.evaluation_date else '',
                record.remarks or '',
                record.created_at.isoformat(sep=' ') if record.created_at else '',
                record.updated_at.isoformat(sep=' ') if record.updated_at else '',
            ])

        return response

    @action(detail=False, methods=['post'], url_path='import')
    def import_records(self, request, *args, **kwargs):
        upload = request.FILES.get('file')
        if not upload:
            return Response({'detail': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)

        file_bytes = upload.read()
        records_data = []
        ext = os.path.splitext(upload.name or '')[1].lower()

        try:
            if ext in ('.xlsx', '.xlsm', '.xltx', '.xltm'):
                records_data = self._read_excel(file_bytes)
            elif ext == '.csv' or not ext:
                decoded = file_bytes.decode('utf-8-sig')
                reader = csv.DictReader(io.StringIO(decoded))
                records_data = list(reader)
            else:
                decoded = file_bytes.decode('utf-8-sig')
                reader = csv.DictReader(io.StringIO(decoded))
                records_data = list(reader)
        except UnicodeDecodeError:
            return Response({'detail': '文件编码必须为UTF-8'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if not records_data:
            return Response({'detail': '导入文件没有数据'}, status=status.HTTP_400_BAD_REQUEST)

        reader_fieldnames = records_data[0].keys() if isinstance(records_data[0], dict) else []
        required_columns = {
            'id',
            'department_id',
            'department_name',
            'personnel_id',
            'personnel_name',
            'item_description',
            'bonus_score',
            'deduction_score',
            'evaluation_date',
        }
        missing_columns = required_columns - set(reader_fieldnames)
        if missing_columns:
            return Response(
                {'detail': f'缺少必要的列: {", ".join(sorted(missing_columns))}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        records_to_create = []
        seen_ids = set()
        errors = []

        for idx, row in enumerate(records_data, start=2):
            try:
                if not isinstance(row, dict):
                    raise ValueError('数据格式不正确')

                record_id = int(row['id']) if row.get('id') else None
                if record_id in seen_ids:
                    raise ValueError('表中存在重复的记录 ID')
                seen_ids.add(record_id)

                department = self._resolve_department(row.get('department_id'), row.get('department_name'))
                personnel = self._resolve_personnel(row.get('personnel_id'), row.get('personnel_name'))

                evaluation_date = datetime.strptime(row['evaluation_date'], '%Y-%m-%d').date()
                bonus_score = Decimal(row.get('bonus_score') or '0')
                deduction_score = Decimal(row.get('deduction_score') or '0')
                remarks = row.get('remarks', '')

                created_at = self._parse_datetime(row.get('created_at'))
                updated_at = self._parse_datetime(row.get('updated_at'))

                record = EvaluationRecord(
                    id=record_id,
                    department=department,
                    personnel=personnel,
                    item_description=row.get('item_description', ''),
                    bonus_score=bonus_score,
                    deduction_score=deduction_score,
                    total_score=bonus_score - deduction_score,
                    evaluation_date=evaluation_date,
                    remarks=remarks,
                    created_at=created_at or timezone.now(),
                    updated_at=updated_at or timezone.now(),
                )
                records_to_create.append(record)
            except Exception as exc:  # pylint: disable=broad-except
                errors.append(f'第 {idx} 行: {exc}')

        if errors:
            return Response({'detail': '导入失败', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            EvaluationRecord.objects.all().delete()
            EvaluationRecord.objects.bulk_create(records_to_create)

        return Response({'detail': f'成功导入 {len(records_to_create)} 条考评记录'}, status=status.HTTP_200_OK)

    @staticmethod
    def _parse_datetime(value):
        if not value:
            return None
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%f'):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise ValueError('无法解析日期时间字段')

    @staticmethod
    def _resolve_department(department_id, department_name):
        department = None
        if department_id:
            department = Department.objects.filter(id=department_id).first()
        if not department and department_name:
            department = Department.objects.filter(name=department_name).first()
        if not department:
            raise ValueError('无法匹配部门')
        return department

    @staticmethod
    def _resolve_personnel(personnel_id, personnel_name):
        personnel = None
        if personnel_id:
            personnel = Personnel.objects.filter(id=personnel_id).first()
        if not personnel and personnel_name:
            personnel = Personnel.objects.filter(name=personnel_name).first()
        if not personnel:
            raise ValueError('无法匹配人员')
        return personnel

    @staticmethod
    def _read_excel(file_bytes):
        workbook = load_workbook(filename=io.BytesIO(file_bytes), data_only=True)
        sheet = workbook.active
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            return []
        headers = [
            (str(cell).strip() if cell is not None else '').strip()
            for cell in rows[0]
        ]
        if not any(headers):
            raise ValueError('Excel表头为空')

        records = []
        for row_idx, row in enumerate(rows[1:], start=2):
            if row is None:
                continue
            row_dict = {}
            for col_idx, header in enumerate(headers):
                if not header:
                    continue
                value = row[col_idx] if col_idx < len(row) else None
                header_key = header.strip().lower()
                if isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, date):
                    value = value.strftime('%Y-%m-%d')
                elif isinstance(value, (int, float)) and header_key in {'evaluation_date', 'created_at', 'updated_at'}:
                    value = EvaluationRecordViewSet._excel_date_to_iso(value, header_key != 'evaluation_date')
                elif isinstance(value, Decimal):
                    value = str(value)
                elif isinstance(value, float):
                    formatted = format(value, 'f')
                    if '.' in formatted:
                        formatted = formatted.rstrip('0').rstrip('.')
                    value = formatted
                row_dict[header] = '' if value is None else value
            if any(value not in (None, '') for value in row_dict.values()):
                records.append(row_dict)
        return records

    @staticmethod
    def _excel_date_to_iso(excel_value, include_time):
        try:
            float_value = float(excel_value)
        except (TypeError, ValueError) as exc:
            raise ValueError('无法解析Excel日期') from exc
        base_date = datetime(1899, 12, 30)
        delta = timedelta(days=float_value)
        result = base_date + delta
        if include_time:
            return result.strftime('%Y-%m-%d %H:%M:%S')
        return result.strftime('%Y-%m-%d')
