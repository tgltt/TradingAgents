

## 安装

安装包
```text
    安装命令    
    pip install xxxx.tar.gz
```

## 使用
### 代码示例1
```python
import sxsc_tushare as ts
ts.set_token('xxxxxxxxxxxxxxxxxx')
api = ts.get_api(env='qa')
df = api.user()
print(df)
```

### 代码示例2
```python
import sxsc_tushare as ts
api = ts.get_api(token='xxxxxxxxxxxxxxxxxx', env='qa')
df = api.user()
print(df)
```

## 升级日志
20230104，升级山西证券
    ```
    用参数区分API环境地址，
        qa 对应内网地址
        prd 对应公网地址
    ```

20221230，发布山西证券
    ```
    首次发布
    ```