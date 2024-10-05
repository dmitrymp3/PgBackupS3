from config import temp_path
import subprocess
import logging

logger = logging.getLogger(__name__)

def do_backup(database, backup_filename):
	"""
	Создает бэкап переданной базы данных, название передается вторым аргументом
	"""
	command = [
        	'pg_dump',
	        '-U', 'postgres',
	        '-F', 'c',  # Формат: custom
	        # '-v',  # Подробный вывод
	        '-d', database,
	        '-f', temp_path + '/' + backup_filename
	    ]
    
   	 # Выполняем команду резервного копирования
	try:
		subprocess.run(command, check=True)
		logger.info(f'База данных {database} успешно сохранена {temp_path + "/" + backup_filename}')
	except subprocess.CalledProcessError as e:
		logger.critical(f'Ошибка при резервном копировании базы данных: {e}')
		logger.critical(repr(e))

def check_db() -> bool:
	"""
	Получаем список всех БД и убеждаемся, что присутствуют все из конфига
	"""
	return True