# Конфигурация s3-клиента
boto_config = {
    'region_name'           : 'ru-1',
    'api_version'           : None,
    'use_ssl'               : True,
    'verify'                : None,
    'endpoint_url'          : 'https://s3.timeweb.com',
    'aws_access_key_id'     : '<i_am_groot>',
    'aws_secret_access_key' : '<secret_key>',
    'aws_session_token'     : None,
    'config'                : None,
}

# Идентификатор бакета, в который будем класть резервные копии
s3_bucket = '<bucket_id>'

# Список баз данных для бэкапа в формате множества
db_list = {'buh', 'zup', 'zup3', 'ut11', 'unf'} # ЗАМЕНИТЕ НА СВОИ

# Папка, где будут временно размещены созданные бэкапы перед загрузкой в s3. Внимание! Автоматически очищается целиком.
temp_path = 'temp'
