# cookiecutter-tendata-python

## 使用步骤

### 1. 安装 Cookiecutter

```shell script
pip install cookiecutter
```

### 2. 创建项目

```shell script
cookiecutter http://git.tendata.com.cn/tendata/bigdata/cookiecutter-tendata-python.git
```

根据提示输入项目基础信息配置

### 3. 开始开发


## Note

由于 isort 解析带有 `{%%}` 内容的文件出现错误，所以采用 black 做项目格式化。生成后的项目模板仍然内置 `isort` 和 `flake8`。 `black` 
暂时还未纳入技术栈。
