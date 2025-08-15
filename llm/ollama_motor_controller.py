import json
import requests
from typing import Dict, List, Optional, Any
from loguru import logger


class OllamaMotorController:
    """电机控制器 - 使用Ollama本地大模型function calling功能"""
    
    def __init__(self, model: str = "qwen2.5:7b-instruct", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.motors = {
            "motor_1": {"angle": 0, "speed": 0, "status": "idle"},
            "motor_2": {"angle": 0, "speed": 0, "status": "idle"},
            "motor_3": {"angle": 0, "speed": 0, "status": "idle"}
        }
        
        # 定义function calling的工具函数
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "control_motor",
                    "description": "控制指定电机的旋转角度和速度",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "motor_id": {
                                "type": "string",
                                "description": "电机ID (motor_1, motor_2, motor_3)",
                                "enum": ["motor_1", "motor_2", "motor_3"]
                            },
                            "angle": {
                                "type": "number",
                                "description": "目标旋转角度 (度, -180到180)",
                                "minimum": -180,
                                "maximum": 180
                            },
                            "speed": {
                                "type": "number",
                                "description": "旋转速度 (度/秒, 1到100)",
                                "minimum": 1,
                                "maximum": 100
                            }
                        },
                        "required": ["motor_id", "angle"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_motor_status",
                    "description": "获取指定电机的当前状态",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "motor_id": {
                                "type": "string",
                                "description": "电机ID (motor_1, motor_2, motor_3)",
                                "enum": ["motor_1", "motor_2", "motor_3"]
                            }
                        },
                        "required": ["motor_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "stop_motor",
                    "description": "停止指定电机的运动",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "motor_id": {
                                "type": "string",
                                "description": "电机ID (motor_1, motor_2, motor_3)",
                                "enum": ["motor_1", "motor_2", "motor_3"]
                            }
                        },
                        "required": ["motor_id"]
                    }
                }
            }
        ]
        
        logger.info(f"Ollama电机控制器初始化完成, 模型: {model}")
    
    def call_ollama(self, user_message: str) -> Dict[str, Any]:
        """调用Ollama API"""
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个电机控制助手。用户会用自然语言描述想要控制的电机动作，你需要调用相应的函数来执行控制。请严格按照JSON格式返回function calling。"
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "tools": self.tools,
            "tool_choice": "auto",
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"调用Ollama API失败: {e}")
            return {"error": str(e)}
    
    def control_motor(self, motor_id: str, angle: float, speed: float = 50) -> Dict[str, Any]:
        """控制电机旋转到指定角度"""
        logger.info(f"控制电机 {motor_id} 旋转到 {angle}度，速度 {speed}度/秒")
        
        return {
            "success": True,
            "motor_id": motor_id,
            "target_angle": angle,
            "speed": speed,
            "message": f"电机 {motor_id} 开始旋转到 {angle}度"
        }
    
    def get_motor_status(self, motor_id: str) -> Dict[str, Any]:
        """获取电机状态"""
        if motor_id not in self.motors:
            return {"success": False, "error": f"无效的电机ID: {motor_id}"}
        
        return {
            "success": True,
            "motor_id": motor_id,
            "status": self.motors[motor_id]
        }
    
    def stop_motor(self, motor_id: str) -> Dict[str, Any]:
        """停止电机运动"""
        if motor_id not in self.motors:
            return {"success": False, "error": f"无效的电机ID: {motor_id}"}
        
        self.motors[motor_id]["status"] = "stopped"
        logger.info(f"停止电机 {motor_id}")
        
        return {
            "success": True,
            "motor_id": motor_id,
            "message": f"电机 {motor_id} 已停止"
        }
    
    def process_ollama_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """处理Ollama的响应"""
        if "error" in response:
            return {"success": False, "error": response["error"]}
        
        try:
            message = response.get("message", {})
            tool_calls = message.get("tool_calls", [])
            
            if not tool_calls:
                # 如果没有tool_calls，尝试从content中解析
                content = message.get("content", "")
                logger.warning(f"Ollama未返回tool_calls，尝试解析content: {content}")
                return {"success": False, "error": "模型未返回有效的function calling"}
            
            results = []
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                raw_args = tool_call["function"]["arguments"]
                if isinstance(raw_args, str):
                    arguments = json.loads(raw_args)
                else:
                    arguments = raw_args
                
                if function_name == "control_motor":
                    result = self.control_motor(
                        arguments["motor_id"],
                        arguments["angle"],
                        arguments.get("speed", 50)
                    )
                elif function_name == "get_motor_status":
                    result = self.get_motor_status(arguments["motor_id"])
                elif function_name == "stop_motor":
                    result = self.stop_motor(arguments["motor_id"])
                else:
                    result = {"success": False, "error": f"未知函数: {function_name}"}
                
                results.append({
                    "function": function_name,
                    "arguments": arguments,
                    "result": result
                })
            
            return {
                "success": True,
                "results": results,
                "message": "命令执行完成"
            }
            
        except Exception as e:
            logger.error(f"处理Ollama响应失败: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_natural_language_command(self, command: str) -> Dict[str, Any]:
        """执行自然语言命令"""
        logger.info(f"收到自然语言命令: {command}")

        result = {"success": False}
        count = 0
        while not result["success"] and count < 5:
            # 调用Ollama
            ollama_response = self.call_ollama(command)
            # 处理响应
            result = self.process_ollama_response(ollama_response)
            count += 1
        return result
    
    def get_all_motor_status(self) -> Dict[str, Any]:
        """获取所有电机状态"""
        return {
            "success": True,
            "motors": self.motors
        }
    
    def test_connection(self) -> bool:
        """测试Ollama连接"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama连接测试失败: {e}")
            return False 