#!/usr/bin/env python3
"""
测试简历解析功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from resume_parser import resume_parser

def test_resume_parser_import():
    """测试简历解析器导入"""
    print("🧪 测试简历解析器导入...")
    try:
        print("✅ 简历解析器导入成功!")
        print(f"📁 上传目录: {resume_parser.upload_dir}")
        return True
    except Exception as e:
        print(f"❌ 简历解析器导入失败: {e}")
        return False

def test_ai_parsing():
    """测试AI解析功能"""
    print("\n🧪 测试AI解析功能...")
    
    # 模拟简历文本
    sample_resume = """
    张三
    邮箱: zhangsan@example.com
    电话: 13812345678
    
    教育背景:
    2018-2022 北京大学 计算机科学与技术 本科
    
    工作经验:
    2022-2025 阿里巴巴 Python开发工程师
    - 负责后端API开发
    - 使用Django、Flask框架
    - 参与微服务架构设计
    
    技能:
    Python, Django, Flask, MySQL, Redis, Docker
    """
    
    try:
        result = resume_parser.parse_resume_with_ai(sample_resume)
        
        print("✅ AI解析测试成功!")
        print(f"📝 解析结果:")
        for key, value in result.items():
            if value:
                print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI解析测试失败: {e}")
        return False

def test_empty_data_structure():
    """测试空数据结构"""
    print("\n🧪 测试空数据结构...")
    
    try:
        empty_data = resume_parser.get_empty_candidate_data()
        
        expected_keys = [
            "name", "email", "phone", "education", 
            "experience", "skills", "current_position", 
            "expected_salary", "summary"
        ]
        
        for key in expected_keys:
            if key not in empty_data:
                print(f"❌ 缺少字段: {key}")
                return False
        
        print("✅ 空数据结构测试成功!")
        print(f"📝 包含字段: {list(empty_data.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 空数据结构测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎯 开始测试简历解析功能...")
    print("=" * 50)
    
    tests = [
        test_resume_parser_import,
        test_empty_data_structure,
        test_ai_parsing
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 测试完成: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("✅ 简历解析功能正常!")
    else:
        print("⚠️ 部分测试失败，请检查配置")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)