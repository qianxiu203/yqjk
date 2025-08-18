#!/usr/bin/env python3
"""
舆情监控平台部署脚本
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


class Deployer:
    """部署器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        
    def log(self, message, level="INFO"):
        """日志输出"""
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "WARNING": "⚠️ ",
            "ERROR": "❌"
        }
        print(f"{prefix.get(level, '')} {message}")
    
    def run_command(self, command, cwd=None, check=True):
        """执行命令"""
        self.log(f"执行命令: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=check
            )
            if result.stdout:
                print(result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"命令执行失败: {e}", "ERROR")
            if e.stderr:
                print(e.stderr)
            raise
    
    def check_python(self):
        """检查Python版本"""
        self.log("检查Python版本...")
        if sys.version_info < (3, 8):
            self.log(f"Python版本过低: {sys.version}", "ERROR")
            return False
        self.log(f"Python版本检查通过: {sys.version}", "SUCCESS")
        return True
    
    def create_virtual_environment(self):
        """创建虚拟环境"""
        self.log("创建虚拟环境...")
        
        if self.venv_path.exists():
            self.log("虚拟环境已存在，跳过创建", "WARNING")
            return True
        
        try:
            self.run_command(f"python -m venv {self.venv_path}")
            self.log("虚拟环境创建成功", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"创建虚拟环境失败: {e}", "ERROR")
            return False
    
    def get_pip_command(self):
        """获取pip命令"""
        if os.name == 'nt':  # Windows
            return str(self.venv_path / "Scripts" / "pip")
        else:  # Linux/Mac
            return str(self.venv_path / "bin" / "pip")
    
    def get_python_command(self):
        """获取Python命令"""
        if os.name == 'nt':  # Windows
            return str(self.venv_path / "Scripts" / "python")
        else:  # Linux/Mac
            return str(self.venv_path / "bin" / "python")
    
    def install_dependencies(self):
        """安装依赖"""
        self.log("安装依赖包...")
        
        pip_cmd = self.get_pip_command()
        
        try:
            # 升级pip
            self.run_command(f"{pip_cmd} install --upgrade pip")
            
            # 安装依赖
            self.run_command(f"{pip_cmd} install -r requirements.txt")
            
            self.log("依赖安装成功", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"安装依赖失败: {e}", "ERROR")
            return False
    
    def create_directories(self):
        """创建必要目录"""
        self.log("创建目录结构...")
        
        directories = ["logs", "static", "data", "backups"]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
            self.log(f"创建目录: {directory}")
        
        self.log("目录创建完成", "SUCCESS")
        return True
    
    def setup_configuration(self):
        """设置配置"""
        self.log("设置配置文件...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if not env_file.exists():
            if env_example.exists():
                shutil.copy(env_example, env_file)
                self.log("已从示例文件创建.env配置", "SUCCESS")
            else:
                self.log(".env配置文件已存在", "WARNING")
        
        self.log("请检查并修改.env文件中的配置", "WARNING")
        return True
    
    def test_installation(self):
        """测试安装"""
        self.log("测试安装...")
        
        python_cmd = self.get_python_command()
        
        try:
            # 运行快速测试
            self.run_command(f"{python_cmd} test_system.py --mode quick")
            self.log("安装测试通过", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"安装测试失败: {e}", "ERROR")
            return False
    
    def create_startup_scripts(self):
        """创建启动脚本"""
        self.log("创建启动脚本...")
        
        python_cmd = self.get_python_command()
        
        # Windows启动脚本
        if os.name == 'nt':
            start_script = self.project_root / "start.bat"
            with open(start_script, 'w', encoding='utf-8') as f:
                f.write(f"""@echo off
echo 启动舆情监控平台...
cd /d "{self.project_root}"
"{python_cmd}" main.py --mode server
pause
""")
            self.log("创建Windows启动脚本: start.bat")
        
        # Linux/Mac启动脚本
        start_script = self.project_root / "start.sh"
        with open(start_script, 'w', encoding='utf-8') as f:
            f.write(f"""#!/bin/bash
echo "启动舆情监控平台..."
cd "{self.project_root}"
"{python_cmd}" main.py --mode server
""")
        
        # 设置执行权限
        if os.name != 'nt':
            os.chmod(start_script, 0o755)
        
        self.log("创建启动脚本: start.sh")
        self.log("启动脚本创建完成", "SUCCESS")
        return True
    
    def create_service_file(self):
        """创建系统服务文件（Linux）"""
        if os.name == 'nt':
            return True  # Windows不需要
        
        self.log("创建系统服务文件...")
        
        python_cmd = self.get_python_command()
        service_content = f"""[Unit]
Description=Sentiment Monitor Platform
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={self.project_root}
ExecStart={python_cmd} main.py --mode server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = self.project_root / "sentiment-monitor.service"
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write(service_content)
        
        self.log("系统服务文件已创建: sentiment-monitor.service")
        self.log("要安装服务，请运行: sudo cp sentiment-monitor.service /etc/systemd/system/", "WARNING")
        return True
    
    def deploy(self):
        """执行部署"""
        self.log("开始部署舆情监控平台")
        self.log("=" * 50)
        
        steps = [
            ("检查Python版本", self.check_python),
            ("创建虚拟环境", self.create_virtual_environment),
            ("安装依赖包", self.install_dependencies),
            ("创建目录结构", self.create_directories),
            ("设置配置文件", self.setup_configuration),
            ("创建启动脚本", self.create_startup_scripts),
            ("创建服务文件", self.create_service_file),
            ("测试安装", self.test_installation),
        ]
        
        for step_name, step_func in steps:
            self.log(f"执行步骤: {step_name}")
            try:
                if not step_func():
                    self.log(f"步骤失败: {step_name}", "ERROR")
                    return False
            except Exception as e:
                self.log(f"步骤异常: {step_name} - {e}", "ERROR")
                return False
        
        self.log("=" * 50)
        self.log("部署完成！", "SUCCESS")
        self.log("=" * 50)
        
        # 输出使用说明
        self.print_usage_instructions()
        
        return True
    
    def print_usage_instructions(self):
        """打印使用说明"""
        python_cmd = self.get_python_command()
        
        print("\n📋 使用说明:")
        print("-" * 30)
        print("1. 检查并修改配置文件:")
        print(f"   编辑 {self.project_root}/.env")
        print()
        print("2. 启动应用:")
        if os.name == 'nt':
            print("   双击 start.bat 或运行:")
        print(f"   {python_cmd} main.py --mode server")
        print()
        print("3. 访问Web界面:")
        print("   http://localhost:8000")
        print()
        print("4. 查看API文档:")
        print("   http://localhost:8000/docs")
        print()
        print("5. 运行测试:")
        print(f"   {python_cmd} test_system.py")


def main():
    """主函数"""
    deployer = Deployer()
    
    try:
        success = deployer.deploy()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 部署被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 部署过程中出现错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
