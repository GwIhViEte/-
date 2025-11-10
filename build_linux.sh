#!/bin/bash
# AI_Novel_Generator - Linux自动构建脚本
# 此脚本用于本地构建Linux可执行文件

echo "========================================"
echo "AI_Novel_Generator - Linux构建脚本"
echo "========================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python"
    exit 1
fi

echo "检测到Python，版本信息："
python3 --version
echo

# 检查虚拟环境
if [ -d ".venv" ]; then
    echo "找到虚拟环境，正在激活..."
    source .venv/bin/activate
else
    echo "虚拟环境未找到，正在创建..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

echo
echo "正在安装/更新依赖包..."
echo

# 升级pip
python -m pip install --upgrade pip

# 安装系统依赖（如果需要）
if command -v apt-get; then
    echo "检查并安装系统依赖..."
    sudo apt-get update
    sudo apt-get install -y python3-tk python3-dev p7zip-full 2>/dev/null || true
fi

# 安装基础依赖
pip install -r requirements.txt

# 安装构建依赖
pip install pyinstaller
pip install aiohttp pillow

echo
echo "正在构建可执行文件..."
echo

# 使用配置文件构建
python build_config.py

# 执行PyInstaller构建
pyinstaller --onefile --name "AI_Novel_Generator" main.py

if [ $? -ne 0 ]; then
    echo "构建失败！"
    exit 1
fi

echo
echo "正在创建发布包..."
echo

# 创建发布目录
mkdir -p dist/release

# 复制文件到发布目录
cp "dist/AI_Novel_Generator" "dist/release/"
cp main.py "dist/release/"
cp main_wrapper.py "dist/release/"
cp README*.md "dist/release/"
cp LICENSE.txt "dist/release/" 2>/dev/null || true

# 复制目录
cp -r core "dist/release/"
cp -r utils "dist/release/"
cp -r templates "dist/release/"
cp -r ui "dist/release/"
cp -r resources "dist/release/" 2>/dev/null || true
cp -r example_prompts "dist/release/" 2>/dev/null || true

# 创建启动脚本
cat > "dist/release/run.sh" << 'EOF'
#!/bin/bash
echo "AI Novel Generator Launcher"
echo "==========================="
./AI_Novel_Generator
EOF

chmod +x "dist/release/run.sh"

# 创建构建信息
cat > "dist/release/build_info.txt" << EOF
构建信息
=================
构建日期: $(date)
构建时间: $(date +%T)
操作系统: Linux
Python版本: $(python --version)
EOF

echo
echo "正在创建TAR.GZ压缩包..."
echo

cd dist/release
tar -czf "../AI_Novel_Generator_linux.tar.gz" *

cd ../..

echo
echo "========================================"
echo "构建完成！"
echo "========================================"
echo
echo "可执行文件: dist/AI_Novel_Generator"
echo "发布包: dist/AI_Novel_Generator_linux.tar.gz"
echo "发布目录: dist/release/"
echo

# 询问是否运行
read -p "是否立即运行程序？(y/n): " choice
if [[ $choice == "y" || $choice == "Y" ]]; then
    echo "正在启动程序..."
    cd dist/release
    ./run.sh
fi