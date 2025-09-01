from langchain.tools import tool
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any
import sqlite3
from pathlib import Path

# 模拟数据库连接（实际项目中应该连接真实数据库）
DB_PATH = ":memory:"  # 使用内存数据库进行演示

@tool
def get_current_date() -> str:
    """获取当前日期，格式为YYYY-MM-DD"""
    return datetime.now().strftime("%Y-%m-%d")

@tool
def get_metric_definition(metric_name: str) -> str:
    """
    获取指标定义和计算逻辑
    
    Args:
        metric_name: 指标名称
    
    Returns:
        str: 指标定义、计算方法和数据来源
    """
    metric_definitions = {
        "user_count": {
            "name": "用户数量",
            "definition": "统计活跃用户数量，活跃用户定义为最近30天内有登录行为的用户",
            "calculation": "COUNT(DISTINCT user_id) FROM user_activity WHERE last_login >= DATE('now', '-30 days')",
            "data_source": "user_activity表"
        },
        "order_count": {
            "name": "订单数量", 
            "definition": "统计每日成功支付的订单数量",
            "calculation": "COUNT(*) FROM orders WHERE status = 'completed' AND order_date = CURRENT_DATE",
            "data_source": "orders表"
        },
        "revenue": {
            "name": "收入",
            "definition": "统计每日总收入，包括所有成功支付的订单金额",
            "calculation": "SUM(amount) FROM orders WHERE status = 'completed' AND order_date = CURRENT_DATE",
            "data_source": "orders表"
        },
        "conversion_rate": {
            "name": "转化率",
            "definition": "用户从浏览到购买的转化比例",
            "calculation": "(订单用户数 / 浏览用户数) * 100",
            "data_source": "user_behavior表和orders表"
        }
    }
    
    if metric_name in metric_definitions:
        metric = metric_definitions[metric_name]
        return f"""指标名称: {metric['name']}
定义: {metric['definition']}
计算方法: {metric['calculation']}
数据来源: {metric['data_source']}"""
    else:
        return f"未找到指标 '{metric_name}' 的定义。可用指标: {', '.join(metric_definitions.keys())}"

@tool
def get_table_metadata(table_name: str) -> str:
    """
    获取表的详细结构信息、索引和关系
    
    Args:
        table_name: 表名称
    
    Returns:
        str: 表的完整结构信息，包括字段、类型、约束、索引和外键关系
    """
    table_metadata = {
        "users": {
            "description": "用户基本信息表",
            "columns": [
                {"name": "id", "type": "INTEGER", "primary_key": True, "nullable": False},
                {"name": "name", "type": "VARCHAR(100)", "nullable": False},
                {"name": "email", "type": "VARCHAR(255)", "unique": True, "nullable": False},
                {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
            ],
            "indexes": ["idx_users_email", "idx_users_created_at"],
            "relationships": [
                {"related_table": "orders", "foreign_key": "user_id", "relationship": "一对多"}
            ]
        },
        "orders": {
            "description": "订单信息表", 
            "columns": [
                {"name": "id", "type": "INTEGER", "primary_key": True},
                {"name": "user_id", "type": "INTEGER", "foreign_key": "users(id)", "nullable": False},
                {"name": "amount", "type": "DECIMAL(10,2)", "nullable": False},
                {"name": "status", "type": "VARCHAR(20)", "nullable": False, "check": "status IN ('pending', 'completed', 'cancelled')"},
                {"name": "order_date", "type": "DATE", "nullable": False},
                {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
            ],
            "indexes": ["idx_orders_user_id", "idx_orders_order_date", "idx_orders_status"],
            "relationships": [
                {"related_table": "users", "foreign_key": "user_id", "relationship": "多对一"},
                {"related_table": "order_items", "foreign_key": "order_id", "relationship": "一对多"}
            ]
        },
        "products": {
            "description": "产品信息表",
            "columns": [
                {"name": "id", "type": "INTEGER", "primary_key": True},
                {"name": "name", "type": "VARCHAR(200)", "nullable": False},
                {"name": "price", "type": "DECIMAL(10,2)", "nullable": False},
                {"name": "category", "type": "VARCHAR(50)", "nullable": False},
                {"name": "stock", "type": "INTEGER", "default": 0},
                {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
            ],
            "indexes": ["idx_products_category", "idx_products_price"]
        }
    }
    
    if table_name in table_metadata:
        table = table_metadata[table_name]
        result = [f"表名: {table_name}", f"描述: {table['description']}", "", "字段结构:"]
        
        for col in table['columns']:
            col_info = [f"  - {col['name']}: {col['type']}"]
            if col.get('primary_key'):
                col_info.append("主键")
            if col.get('foreign_key'):
                col_info.append(f"外键 -> {col['foreign_key']}")
            if col.get('unique'):
                col_info.append("唯一约束")
            if col.get('nullable') is False:
                col_info.append("非空")
            result.append(" ".join(col_info))
        
        if table.get('indexes'):
            result.extend(["", "索引:", *[f"  - {idx}" for idx in table['indexes']]])
        
        if table.get('relationships'):
            result.extend(["", "表关系:"])
            for rel in table['relationships']:
                result.append(f"  - {rel['relationship']} -> {rel['related_table']} ({rel.get('foreign_key', '')})")
        
        return "\n".join(result)
    else:
        available_tables = ", ".join(table_metadata.keys())
        return f"未找到表 '{table_name}' 的元数据信息。可用表: {available_tables}"

@tool
def sql_execute(query: str) -> str:
    """
    执行SQL查询并返回格式化结果
    
    Args:
        query: SQL查询语句（SELECT语句）
    
    Returns:
        str: 查询结果，包括行数和格式化数据
    """
    # 简单的SQL验证（实际项目中应该更严格）
    query_lower = query.lower().strip()
    if not query_lower.startswith('select'):
        return "错误: 只支持SELECT查询语句"
    
    try:
        # 使用内存SQLite数据库进行演示
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建演示数据
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('pending', 'completed', 'cancelled')),
                order_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # 插入一些演示数据
        cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, '张三', 'zhangsan@example.com')")
        cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, '李四', 'lisi@example.com')")
        cursor.execute("INSERT OR IGNORE INTO orders (id, user_id, amount, status, order_date) VALUES (1, 1, 100.0, 'completed', '2024-01-15')")
        cursor.execute("INSERT OR IGNORE INTO orders (id, user_id, amount, status, order_date) VALUES (2, 2, 200.0, 'completed', '2024-01-15')")
        
        # 执行用户查询
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        conn.commit()
        conn.close()
        
        if not results:
            return "查询成功，但未返回任何数据"
        
        # 格式化结果
        output = [f"执行SQL查询: {query}", f"返回行数: {len(results)}", "", "结果:"]
        
        # 显示列名
        output.append(" | ".join(columns))
        output.append("-" * (len(" | ".join(columns)) + 10))
        
        # 显示数据（限制最多显示10行）
        for row in results[:10]:
            output.append(" | ".join(str(cell) for cell in row))
        
        if len(results) > 10:
            output.append(f"... (还有 {len(results) - 10} 行未显示)")
        
        return "\n".join(output)
        
    except sqlite3.Error as e:
        return f"SQL执行错误: {str(e)}"
    except Exception as e:
        return f"执行查询时发生错误: {str(e)}"

@tool
def get_all_metric_names() -> str:
    """
    获取所有可用的指标名称及其简要描述
    
    Returns:
        str: 所有指标的列表和描述
    """
    metrics = {
        "user_count": "用户数量 - 统计活跃用户数量",
        "order_count": "订单数量 - 统计每日成功支付的订单数量", 
        "revenue": "收入 - 统计每日总收入",
        "conversion_rate": "转化率 - 用户从浏览到购买的转化比例",
        "average_order_value": "平均订单价值 - 每个订单的平均金额",
        "customer_acquisition_cost": "客户获取成本 - 获取新客户的成本",
        "retention_rate": "留存率 - 用户的持续使用比例",
        "lifetime_value": "用户生命周期价值 - 单个用户在整个使用期间产生的总价值"
    }
    
    result = ["可用指标:", ""]
    for name, description in metrics.items():
        result.append(f"• {name}: {description}")
    
    result.extend(["", "使用 get_metric_definition(metric_name) 获取详细定义和计算方法"])
    return "\n".join(result)

@tool
def analyze_data_trend(metric_name: str, days: int = 30) -> str:
    """
    分析指标的历史趋势
    
    Args:
        metric_name: 指标名称
        days: 分析的天数范围
    
    Returns:
        str: 指标的趋势分析报告
    """
    # 模拟趋势分析（实际项目中应该查询真实数据）
    trend_data = {
        "user_count": {
            "current": 1250,
            "previous": 1200,
            "trend": "上升",
            "change_percent": 4.17,
            "insights": "用户数量稳步增长，可能得益于最近的营销活动"
        },
        "order_count": {
            "current": 89,
            "previous": 85, 
            "trend": "上升",
            "change_percent": 4.71,
            "insights": "订单数量略有增长，建议关注转化率优化"
        },
        "revenue": {
            "current": 15680.50,
            "previous": 14890.25,
            "trend": "上升", 
            "change_percent": 5.31,
            "insights": "收入增长良好，平均订单价值有所提升"
        }
    }
    
    if metric_name in trend_data:
        data = trend_data[metric_name]
        return f"""{metric_name} 趋势分析 (最近{days}天):

当前值: {data['current']}
前期值: {data['previous']} 
趋势: {data['trend']} ({data['change_percent']}%)

洞察: {data['insights']}

建议: 继续监控该指标，如趋势持续可考虑扩大相关投入"""
    else:
        return f"暂不支持指标 '{metric_name}' 的趋势分析。可用指标: {', '.join(trend_data.keys())}"

@tool
def get_data_quality_report(table_name: str) -> str:
    """
    获取表的数据质量报告
    
    Args:
        table_name: 表名称
    
    Returns:
        str: 数据质量评估报告
    """
    quality_reports = {
        "users": {
            "completeness": 98.5,
            "accuracy": 96.2,
            "consistency": 97.8,
            "timeliness": 99.1,
            "issues": ["少量邮箱格式不规范", "部分用户缺少最后登录时间"],
            "recommendations": ["添加邮箱格式验证", "完善用户信息收集流程"]
        },
        "orders": {
            "completeness": 99.2, 
            "accuracy": 98.7,
            "consistency": 99.5,
            "timeliness": 98.9,
            "issues": ["极少数订单状态异常"],
            "recommendations": ["加强订单状态流转监控"]
        }
    }
    
    if table_name in quality_reports:
        report = quality_reports[table_name]
        result = [f"{table_name} 表数据质量报告:", ""]
        result.append(f"完整性: {report['completeness']}%")
        result.append(f"准确性: {report['accuracy']}%")
        result.append(f"一致性: {report['consistency']}%")
        result.append(f"及时性: {report['timeliness']}%")
        
        if report['issues']:
            result.extend(["", "发现的问题:"])
            for issue in report['issues']:
                result.append(f"• {issue}")
        
        if report['recommendations']:
            result.extend(["", "改进建议:"])
            for rec in report['recommendations']:
                result.append(f"• {rec}")
        
        result.extend(["", "总体评估: 数据质量良好，建议定期监控"]) 
        return "\n".join(result)
    else:
        return f"暂未生成表 '{table_name}' 的数据质量报告"

@tool
def suggest_analysis(question: str) -> str:
    """
    根据用户问题建议合适的分析方法
    
    Args:
        question: 用户的分析问题
    
    Returns:
        str: 分析建议和方法推荐
    """
    suggestions = {
        "user": ["用户增长趋势分析", "用户分层分析", "用户行为路径分析", "用户留存分析"],
        "order": ["订单趋势分析", "订单金额分布", "订单转化率分析", "客户价值分析"],
        "revenue": ["收入趋势分析", "收入来源分析", "产品收入贡献分析", "客户价值分析"],
        "转化": ["转化漏斗分析", "转化率影响因素分析", "A/B测试结果分析"]
    }
    
    question_lower = question.lower()
    recommended_analyses = []
    
    for keyword, analyses in suggestions.items():
        if keyword in question_lower:
            recommended_analyses.extend(analyses)
    
    if not recommended_analyses:
        recommended_analyses = [
            "趋势分析", "对比分析", "分布分析", 
            "相关性分析", "漏斗分析", "留存分析"
        ]
    
    result = [f"针对问题: {question}", "", "推荐的分析方法:"]
    for analysis in list(set(recommended_analyses))[:5]:  # 去重并取前5个
        result.append(f"• {analysis}")
    
    result.extend(["", "可用工具:", "• get_metric_definition - 获取指标定义", "• sql_execute - 执行数据分析查询", "• analyze_data_trend - 分析数据趋势"])
    return "\n".join(result)