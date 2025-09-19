#!/bin/bash
# 自动部署Django ASGI服务器脚本

set -e  # 遇到错误立即退出

echo "=== Django ASGI服务器自动部署脚本 ==="
echo "检测并安装必需的软件包..."

# 颜色输出定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
            PKG_MANAGER="apt-get"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
            PKG_MANAGER="yum"
        else
            OS="linux"
            PKG_MANAGER="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then # MacOS 应该？能用？
        OS="macos"
        PKG_MANAGER="brew"
    else
        OS="unknown"
        PKG_MANAGER="unknown"
    fi
    print_message "检测到操作系统: $OS"
}

# 检查并安装Python
check_python() {
    print_step "检查Python安装..."

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_message "Python3 已安装，版本: $PYTHON_VERSION"
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        if [[ $PYTHON_VERSION == 3.* ]]; then
            print_message "Python 已安装，版本: $PYTHON_VERSION"
            PYTHON_CMD="python"
        else
            print_error "需要Python 3.x，当前版本: $PYTHON_VERSION"
            install_python
        fi
    else
        print_warning "未检测到Python，开始安装..."
        install_python
    fi
}

# 安装Python
install_python() {
    case $OS in
        "debian")
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
            PYTHON_CMD="python3"
            ;;
        "redhat")
            sudo yum install -y python3 python3-pip
            PYTHON_CMD="python3"
            ;;
        "macos")
            if ! command -v brew &> /dev/null; then
                print_error "请先安装Homebrew: https://brew.sh/"
                exit 1
            fi
            brew install python3
            PYTHON_CMD="python3"
            ;;
        *)
            print_error "不支持的操作系统，请手动安装Python 3.8+"
            exit 1
            ;;
    esac
    print_message "Python安装完成"
}

# 检查并安装pip
check_pip() {
    print_step "检查pip安装..."

    if command -v pip3 &> /dev/null; then
        print_message "pip3 已安装"
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        print_message "pip 已安装"
        PIP_CMD="pip"
    else
        print_warning "pip未安装，开始安装..."
        install_pip
    fi
}

# 安装pip
install_pip() {
    case $OS in
        "debian")
            sudo apt-get install -y python3-pip
            PIP_CMD="pip3"
            ;;
        "redhat")
            sudo yum install -y python3-pip
            PIP_CMD="pip3"
            ;;
        "macos")
            # pip通常随Python一起安装
            PIP_CMD="pip3"
            ;;
        *)
            # 使用get-pip.py脚本
            curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            $PYTHON_CMD get-pip.py
            rm get-pip.py
            PIP_CMD="pip"
            ;;
    esac
    print_message "pip安装完成"
}

# 创建和激活虚拟环境
setup_virtual_env() {
    print_step "设置Python虚拟环境..."

    if [ ! -d "venv" ]; then
        print_message "创建虚拟环境..."
        $PYTHON_CMD -m venv venv
        print_message "虚拟环境创建完成"
    else
        print_message "虚拟环境已存在"
    fi

    # 激活虚拟环境
    source venv/bin/activate
    print_message "虚拟环境已激活"

    # 升级pip
    pip install --upgrade pip
}

# 安装Python依赖
install_dependencies() {
    print_step "安装Python依赖包..."

    if [ -f "requirements.txt" ]; then
        print_message "从requirements.txt安装依赖..."
        pip install -r requirements.txt
    else
        print_message "requirements.txt不存在，安装基础依赖..."
        pip install Django>=5.2.0 djangorestframework django-cors-headers gunicorn>=23.0.0 uvicorn>=0.35.0

        # 创建requirements.txt
        pip freeze > requirements.txt
        print_message "已生成requirements.txt文件"
    fi

    print_message "依赖包安装完成"
}

# 初始化数据库
setup_database() {
    print_step "初始化数据库..."

    # 运行数据库迁移
    print_message "应用数据库迁移..."
    python manage.py makemigrations
    python manage.py migrate

    # 创建超级用户（如果不存在）
    print_message "检查超级用户..."
    python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('超级用户已创建 - 用户名: admin, 密码: admin123')
else:
    print('超级用户已存在')
"
}

# 收集静态文件
collect_static() {
    print_step "收集静态文件..."
    python manage.py collectstatic --noinput --clear
    print_message "静态文件收集完成"
}

# 检查端口占用
check_port() {
    PORT=${1:-8000}
    if command -v lsof &> /dev/null && lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "端口 $PORT 已被占用，尝试终止进程..."
        PID=$(lsof -ti:$PORT)
        if [ ! -z "$PID" ]; then
            kill -9 $PID
            sleep 2
            print_message "端口 $PORT 已释放"
        fi
    fi
}

# 启动服务器
start_server() {
    print_step "启动Gunicorn ASGI服务器..."

    # 检查端口
    check_port 8000

    # 启动服务器
    exec gunicorn item_manager.asgi:application \
        --bind 0.0.0.0:8000 \
        --worker-class uvicorn.workers.UvicornWorker \
        --workers 4 \
        --timeout 30 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --reload
}

# 主函数
main() {
    print_message "开始自动部署Django ASGI服务器..."

    # 检测系统环境
    detect_os

    # 检查和安装必要软件
    check_python
    check_pip

    # 设置虚拟环境
    setup_virtual_env

    # 安装依赖
    install_dependencies

    # 初始化数据库
    setup_database

    # 收集静态文件
    collect_static

    # 启动服务器
    print_message "所有准备工作完成，启动服务器..."
    echo ""
    print_message "服务器信息:"
    print_message "- 访问地址: http://localhost:8000"
    print_message "- API地址: http://localhost:8000/api/"
    print_message "- 管理后台: http://localhost:8000/admin/"
    print_message "- 默认管理员: admin / admin123"
    echo ""

    start_server
}

# 错误处理
trap 'print_error "脚本执行失败，请检查错误信息"; exit 1' ERR

# 执行主函数
main "$@"
