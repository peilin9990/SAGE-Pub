# SAGE Core 基础示例

本文档包含了SAGE Core的基础使用示例，展示核心功能的实际应用。

## 快速上手示例

### Hello World

```python
from sage.core.api.local_environment import LocalEnvironment

# 创建执行环境
env = LocalEnvironment("hello_sage")

# 简单的数据处理
data_stream = env.from_batch(["Hello", "SAGE", "World"])
result_stream = data_stream.map(lambda x: x.upper()).filter(lambda x: len(x) > 4)

# 输出结果
result_stream.print("Result: ")

# 提交任务
env.submit()
```

### 基础流处理

```python
import time
from sage.core.api.local_environment import LocalEnvironment

env = LocalEnvironment("basic_streaming")

# 模拟数据流
def generate_stream():
    for i in range(100):
        yield {
            'id': i,
            'timestamp': time.time(),
            'value': i * 2,
            'category': 'A' if i % 2 == 0 else 'B'
        }

# 创建批处理函数来处理分组逻辑
class CategoryAggregator:
    def __init__(self):
        self.groups = {}
    
    def process_item(self, item):
        category = item['category']
        if category not in self.groups:
            self.groups[category] = []
        self.groups[category].append(item)
        return item
    
    def get_aggregated_results(self):
        results = []
        for category, items in self.groups.items():
            filtered_items = [item for item in items if item['value'] > 50]
            if filtered_items:
                avg_value = sum(item['value'] for item in filtered_items) / len(filtered_items)
                results.append({
                    'category': category,
                    'count': len(filtered_items),
                    'avg_value': avg_value
                })
        return results

# 流处理
aggregator = CategoryAggregator()
stream = env.from_batch(list(generate_stream()))

# 过滤并处理数据
filtered_stream = stream.filter(lambda x: x['value'] > 50).map(aggregator.process_item)

# 输出结果
filtered_stream.print("Processed item: ")

# 提交任务
env.submit()

# 打印聚合结果
for category_result in aggregator.get_aggregated_results():
    print(f"Category {category_result['category']}: "
          f"count={category_result['count']}, "
          f"avg={category_result['avg_value']:.2f}")
```

### 文件处理示例

```python
import json
import tempfile
from sage.core.api.local_environment import LocalEnvironment

env = LocalEnvironment("file_processing")

# 创建示例JSON文件
sample_data = [
    {'name': 'Alice', 'age': 25, 'city': 'New York', 'salary': 70000},
    {'name': 'Bob', 'age': 30, 'city': 'San Francisco', 'salary': 85000},
    {'name': 'Charlie', 'age': 35, 'city': 'New York', 'salary': 95000},
    {'name': 'Diana', 'age': 28, 'city': 'Chicago', 'salary': 75000}
]

# 写入临时文件
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    for record in sample_data:
        json.dump(record, f)
        f.write('\n')
    temp_file = f.name

# 处理文件
def read_json_lines(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

# 创建数据分析器
class CityAnalyzer:
    def __init__(self):
        self.city_data = {}
    
    def process_person(self, person):
        city = person['city']
        if city not in self.city_data:
            self.city_data[city] = []
        self.city_data[city].append(person)
        return person
    
    def get_city_analysis(self):
        results = []
        for city, people in self.city_data.items():
            avg_age = sum(p['age'] for p in people) / len(people)
            avg_salary = sum(p['salary'] for p in people) / len(people)
            results.append({
                'city': city,
                'population': len(people),
                'avg_age': avg_age,
                'avg_salary': avg_salary,
                'residents': [p['name'] for p in people]
            })
        return results

# 分析数据
analyzer = CityAnalyzer()
stream = env.from_batch(list(read_json_lines(temp_file)))
processed_stream = stream.map(analyzer.process_person)

# 输出处理结果
processed_stream.print("Processed person: ")

# 提交任务
env.submit()

# 显示分析结果
for city_stats in analyzer.get_city_analysis():
    print(f"\n{city_stats['city']}:")
    print(f"  Population: {city_stats['population']}")
    print(f"  Average age: {city_stats['avg_age']:.1f}")
    print(f"  Average salary: ${city_stats['avg_salary']:,.2f}")
    print(f"  Residents: {', '.join(city_stats['residents'])}")

# 清理
import os
os.unlink(temp_file)
```

### 连接流处理示例

```python
import time
from sage.core.api.local_environment import LocalEnvironment

env = LocalEnvironment("connected_streams")

# 用户数据
user_data = [
    {'user_id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
    {'user_id': 2, 'name': 'Bob', 'email': 'bob@example.com'},
    {'user_id': 3, 'name': 'Charlie', 'email': 'charlie@example.com'}
]

# 事件数据
event_data = [
    {'user_id': 1, 'action': 'login', 'timestamp': time.time() - 300},
    {'user_id': 1, 'action': 'view_page', 'timestamp': time.time() - 250},
    {'user_id': 2, 'action': 'login', 'timestamp': time.time() - 200},
    {'user_id': 1, 'action': 'logout', 'timestamp': time.time() - 150},
    {'user_id': 3, 'action': 'login', 'timestamp': time.time() - 100},
    {'user_id': 2, 'action': 'purchase', 'timestamp': time.time() - 50}
]

# 创建用户活动分析器
class UserActivityJoiner:
    def __init__(self):
        self.users = {}
        self.events = {}
    
    def process_user(self, user):
        self.users[user['user_id']] = user
        return user
    
    def process_event(self, event):
        user_id = event['user_id']
        if user_id not in self.events:
            self.events[user_id] = []
        self.events[user_id].append(event)
        return event
    
    def get_user_activity_summary(self):
        results = []
        for user_id, user in self.users.items():
            user_events = self.events.get(user_id, [])
            last_action = max(user_events, key=lambda e: e['timestamp'])['action'] if user_events else None
            
            results.append({
                'user_name': user['name'],
                'user_email': user['email'],
                'event_count': len(user_events),
                'last_action': last_action,
                'actions': [e['action'] for e in user_events]
            })
        return results

# 处理用户和事件数据
joiner = UserActivityJoiner()

users_stream = env.from_batch(user_data)
events_stream = env.from_batch(event_data)

# 分别处理用户和事件
processed_users = users_stream.map(joiner.process_user)
processed_events = events_stream.map(joiner.process_event)

# 输出处理状态
processed_users.print("Processed user: ")
processed_events.print("Processed event: ")

# 提交任务
env.submit()

# 显示活动摘要
for summary in joiner.get_user_activity_summary():
    print(f"{summary['user_name']} ({summary['user_email']}):")
    print(f"  Events: {summary['event_count']}")
    print(f"  Last action: {summary['last_action']}")
    print(f"  All actions: {', '.join(summary['actions'])}")
```

## 实际应用场景

这些示例展示了SAGE Core的基本功能，可以作为更复杂应用的起点：

- **数据ETL**: 使用map、filter、flatmap进行数据转换
- **实时分析**: 使用流处理功能分析实时数据
- **文件处理**: 批量处理大型文件数据
- **数据关联**: 使用connect和comap操作关联多个数据源

继续探索[高级教程](../kernel/examples/basic_tutorials.md)以了解更复杂的使用场景。
