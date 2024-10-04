import boto3
from botocore.exceptions import ClientError
import logging
from config import boto_config, temp_path, rules_for_backups, databases
# import pprint
from pprint import pprint

logger = logging.getLogger(__name__)

# Убираем логи boto, их слишком много при выгрузке файлов
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('nose').setLevel(logging.WARNING)

# Создаем клиент для коннекта к s3 хранилищу
s3 = boto3.client('s3', **boto_config.return_data())

# Добавим финальный слэш во временную папку, здесь он нужен
temp_folder = f'{temp_path}/'


def upload_file(filename):
    """
    Просто загружает файл в бакет
    """
    s3.upload_file(temp_folder + filename, boto_config.s3_bucket, filename)


def clear_s3():
    """
    Эта функция будет очищать s3 хранилище от старых бэкапов
    1. Получаем список всех бэкапов
    2. Разбиваем их по базам
    3. Разбиваем по типам
    4. Берем из конфига данные о количестве хранимых бэкапов по типам
    5. Определяем бэкапы к удалению
    6. Удаляем бэкапы
    """
    logger.info('Запускаем очистку')
    dict_of_objects: dict = s3.list_objects(Bucket=boto_config.s3_bucket).get('Contents')
    # list_of_objects = list_of_objects.get('Contents')
    objects_by_db = {}

    database_to_delete = []

    # Переформируем массив данных о бэкапах в удобный формат
    for object in dict_of_objects:
        backup_name = object.get('Key')
        database_name: str = backup_name.split('-')[0]
        backup_type: str = backup_name.split('-')[2].replace('.dump', '')

        if database_name not in objects_by_db:
            objects_by_db[database_name] = {}
        if backup_type not in objects_by_db[database_name]:
            objects_by_db[database_name][backup_type] = list()

        objects_by_db[database_name][backup_type].append(backup_name)

    # Проверяем каждую базу
    for database, backups in objects_by_db.items():
        # Получаем количество бэкапов из конфига
        database_rules = rules_for_backups.get(database)
        # Проверяем каждый тип бэкапов
        for type_of_backup, backups in backups.items():
            # Получаем количество хранимых бэкапов для этой базы данных и для этого типа бэкапов (DAILY, MONTHLY)
            counter = database_rules.get(type_of_backup) if database_rules else rules_for_backups['default'][type_of_backup]
            # counter = databases.
            # Если количество бэкапов больше, чем нужно
            if len(backups) > counter:
                database_to_delete.extend(backups[0:-counter])


    for database in database_to_delete:
        try:
            s3.delete_object(Bucket=boto_config.s3_bucket, Key=database)
            logger.info(f'Удален бэкап: {database}')
        except:
            logger.warning(f'Попытка удаления бэкапа {database} была неуспешной.')
    logger.info('Очистка завершена')

def check_s3() -> dict:
    """
    Получаем список бакетов, проверяя соединение с S3
    """
    # Пробуем подключиться к s3 и получить список бакетов
    try:
        buckets_dict = s3.list_buckets()
    except ClientError as e:
        logger.critical('Неправильно указаны учетные данные')
        return False
    
    # Формируем список бакетов для второй проверки
    buckets_list = [bucket.get('Name') for bucket in buckets_dict.get('Buckets')]

    # Проверяем наличие указанного в конфиге бакета
    if boto_config.s3_bucket not in buckets_list:
        logger.critical('Неправильно введен s3 бакет')
        return False
    
    return True