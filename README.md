## 安装
执行以下命令：
```
pip install testes.tar.gz && pip install -r /opt/testes/requirements.txt
```
## 使用
* 按照实际环境修改配置文件testes.ini
```
cat /etc/testes/testes.ini

[DEFAULTS]
# 模版目录
template_dir=/opt/testes/templates
# 生成测试数据的索引前缀
gen_index_prefix=faceid-test
# 生成测试数据的索引类型
gen_index_type=dbjson
# 生成测试数据的规则，可以是default、hour、day
index_gen_type=hour
# 测试数据目录地址
test_data_dir=/opt/testes/test_data
# ES主机IP地址
host=http://localhost:9200
# 查询测试数据的文件名
query_data_name=query_data.csv
# 查询模板名
template_name=query.tem
# 测试索引类型
index_type=dbjson
# 测试索引名
index_name=faceid-test
# 创建索引的测试数据文件名
create_data_name=create_data
# 测试时间
interval=300
# 记录测试日志的时间
log_interval=30
# 测试的客户数
client=100
# 测试日志目录地址
test_logfile_dir=/var/log/testes
# testcase的文件目录
test_file_dir=/opt/testes
# testcase的文件名
test_file_names=es_testcase.py
```

* 在配置文件中指定testcase的信息
```
test_file_dir=/opt/testes
test_file_names=es_testcase.py
```

* 运行以下命令
```
python /opt/testes/main.py
```

* 在配置的测试日志目录地址中，可以看到按照[testcase_class_name]\_[task_name]规则生成的测试日志
