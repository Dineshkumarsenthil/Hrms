try:
    import pymysql
    pymysql.version_info = (2, 2, 1, "final", 0)  # satisfy Django's mysqlclient version check
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
