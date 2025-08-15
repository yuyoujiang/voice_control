#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama安装和配置脚本
帮助用户安装和配置Ollama本地大模型
"""

import os
import sys
import subprocess
import requests
import json
from typing import List, Dict, Any


def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🤖 Ollama 安装和配置助手")
    print("=" * 60)
    print("帮助您安装和配置Ollama本地大模型")
    print("用于AI电机控制系统")
    print("=" * 60)


def check_ollama_installed() -> bool:
    """检查Ollama是否已安装"""
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def install_ollama():
    """安装Ollama"""
    print("📦 正在安装Ollama...")
    
    system = os.name
    if system == "nt":  # Windows
        print("Windows系统请访问 https://ollama.ai/download 下载安装包")
        print("或者使用WSL2运行Linux版本")
        return False
    elif system == "posix":  # Linux/macOS
        try:
            # 使用官方安装脚本
            install_cmd = "curl -fsSL https://ollama.ai/install.sh | sh"
            print(f"执行命令: {install_cmd}")
            
            result = subprocess.run(install_cmd, shell=True, timeout=60)
            if result.returncode == 0:
                print("✅ Ollama安装成功")
                return True
            else:
                print("❌ Ollama安装失败")
                return False
        except Exception as e:
            print(f"❌ 安装过程中出错: {e}")
            return False


def check_ollama_service() -> bool:
    """检查Ollama服务是否运行"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def start_ollama_service():
    """启动Ollama服务"""
    print("🚀 正在启动Ollama服务...")
    
    try:
        # 启动Ollama服务
        subprocess.Popen(["ollama", "serve"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # 等待服务启动
        import time
        for i in range(10):
            if check_ollama_service():
                print("✅ Ollama服务启动成功")
                return True
            time.sleep(1)
            print(f"⏳ 等待服务启动... ({i+1}/10)")
        
        print("❌ Ollama服务启动超时")
        return False
    except Exception as e:
        print(f"❌ 启动服务失败: {e}")
        return False


def get_available_models() -> List[Dict[str, Any]]:
    """获取可用的模型列表"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("models", [])
        return []
    except Exception:
        return []


def download_model(model_name: str) -> bool:
    """下载指定的模型"""
    print(f"📥 正在下载模型: {model_name}")
    
    try:
        result = subprocess.run(["ollama", "pull", model_name], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ 模型 {model_name} 下载成功")
            return True
        else:
            print(f"❌ 模型下载失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ 模型下载超时")
        return False
    except Exception as e:
        print(f"❌ 下载过程中出错: {e}")
        return False


def recommend_models() -> List[str]:
    """推荐适合的模型"""
    return [
        "qwen2.5:7b-instruct",  # 中文支持好，function calling能力强
        "llama3.1:8b-instruct",  # 通用性强，推理能力好
        "mistral:7b-instruct",   # 轻量级，响应速度快
        "codellama:7b-instruct"  # 代码理解能力强
    ]


def test_model_function_calling(model_name: str) -> bool:
    """测试模型的function calling能力"""
    print(f"🧪 测试模型 {model_name} 的function calling能力...")
    
    try:
        # 简单的function calling测试
        test_data = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个电机控制助手。请调用control_motor函数来控制电机。"
                },
                {
                    "role": "user", 
                    "content": "让电机1旋转到90度"
                }
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "control_motor",
                        "description": "控制电机",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "motor_id": {"type": "string"},
                                "angle": {"type": "number"}
                            },
                            "required": ["motor_id", "angle"]
                        }
                    }
                }
            ],
            "tool_choice": "auto"
        }
        
        response = requests.post(
            "http://localhost:11434/api/chat",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", {})
            tool_calls = message.get("tool_calls", [])
            
            if tool_calls:
                print(f"✅ 模型 {model_name} 支持function calling")
                return True
            else:
                print(f"⚠️  模型 {model_name} 可能不支持function calling")
                return False
        else:
            print(f"❌ 测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False


def main():
    """主函数"""
    print_banner()
    
    # 检查Ollama是否已安装
    if not check_ollama_installed():
        print("❌ Ollama未安装")
        choice = input("是否要安装Ollama? (y/n): ").lower()
        if choice == 'y':
            if not install_ollama():
                print("❌ 安装失败，请手动安装Ollama")
                return
        else:
            print("请手动安装Ollama后再运行此脚本")
            return
    else:
        print("✅ Ollama已安装")
    
    # 检查服务是否运行
    if not check_ollama_service():
        print("❌ Ollama服务未运行")
        if not start_ollama_service():
            print("❌ 无法启动Ollama服务")
            return
    else:
        print("✅ Ollama服务正在运行")
    
    # 获取可用模型
    print("\n📋 检查可用模型...")
    available_models = get_available_models()
    
    if available_models:
        print("✅ 已安装的模型:")
        for model in available_models:
            print(f"   • {model.get('name', 'Unknown')}")
    else:
        print("⚠️  未找到已安装的模型")
    
    # 推荐模型
    print("\n💡 推荐的模型:")
    recommended_models = recommend_models()
    for i, model in enumerate(recommended_models, 1):
        print(f"   {i}. {model}")
    
    # 询问用户选择模型
    choice = input("\n请选择要下载的模型 (输入数字或模型名称，回车跳过): ").strip()
    
    if choice:
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(recommended_models):
                selected_model = recommended_models[idx]
            else:
                print("❌ 无效的选择")
                return
        else:
            selected_model = choice
        
        print(f"\n🎯 选择的模型: {selected_model}")
        
        # 下载模型
        if download_model(selected_model):
            # 测试function calling
            test_model_function_calling(selected_model)
        else:
            print("❌ 模型下载失败")
    
    print("\n✅ 配置完成！")
    print("现在可以运行以下命令测试:")
    print(f"python test_ai_motor_control.py --ollama --model {selected_model if 'selected_model' in locals() else 'qwen2.5:7b-instruct'}")


if __name__ == "__main__":
    main() 