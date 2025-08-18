#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama电机控制测试脚本
专门用于测试Ollama本地模型的电机控制功能
"""

import os
import sys
import argparse
import time
from loguru import logger

from motor_controller.myactuator_controller_ollama import MyActuatorControllerOllama
from audio.respeaker import get_asr_result


def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    logger.add(
        "logs/ollama_motor_control.log",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Ollama电机控制系统")
    parser.add_argument("--model", default="qwen2.5:7b-instruct", help="Ollama模型名称")
    parser.add_argument("--url", default="http://localhost:11434", help="Ollama服务地址")
    args = parser.parse_args()
    
    setup_logging()

    # 初始化控制器
    controller = MyActuatorControllerOllama(model=args.model, base_url=args.url)
    	
    # result = controller.execute_natural_language_command("Let motor 3 rotate to 360 degrees")
    # status = controller.get_motor_status("motor_1")
    # if status["success"]:
    #     print(status["status"])
    # print("start running...")
    # time.sleep(2)
    # controller.stop_motor("motor_1")
    # print("running done")
    
    history_command = ""
    while True:
        command = get_asr_result()
        if command and command != history_command:
            history_command = command
            logger.info(f"Received command: {command}")
            try:
                if "BLANK_AUDIO" not in command and "(" not in command and "[" not in command:
                    result = controller.execute_natural_language_command(command)
                else:
                    logger.info("Received blank audio, skipping command execution.")
                    result = {"success": False, "error": "Received blank audio"}
            except Exception as e:
                logger.error(f"执行命令失败: {e}")
                result = {"success": False, "error": str(e)}
            logger.info(f"Command result: {result}")
        else:
            logger.info("No new command received.")
            
        time.sleep(3)  # 模拟处理时间


if __name__ == "__main__":
    main() 
