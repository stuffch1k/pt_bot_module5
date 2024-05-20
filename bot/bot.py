import logging
import re, os
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, ContextTypes
from dotenv import load_dotenv
import paramiko
import os
from os.path import join, dirname
import psycopg2
from psycopg2 import Error
import subprocess

# Загрузка переменных из env файла
load_dotenv()

port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')
host = os.getenv('RM_HOST')
repl_host = os.getenv('DB_REPL_HOST')

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_DATABASE')
TOKEN =  os.getenv('TOKEN')

# Логгирование 
logging.basicConfig(
    filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding="utf-8"
)

# Функция для подключения к машине для исполнения команд Линукса
def get_system_info(command, rm = True):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    hostname = host if rm else repl_host
    client.connect(hostname=hostname, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data

# Функция для подключения к БД и исполнения select и insert скриптов
def db(key, command):
    connection = None
    try:
        connection = psycopg2.connect(user=db_user, password=db_pass,
                                  host=db_host, port=db_port, 
                                  database=db_name)

        cursor = connection.cursor()
        cursor.execute(command)
        if key == "insert":
            connection.commit()
            return "Команда успешно выполнена"
        else:
            data = cursor.fetchall()
            result = []
            for row in data:
                result.append(row)
            return result
    except (Exception, Error) as error:
        logging.error(f"host:{db_host}, db:{db_name}, user: {db_user}, pwd:{db_pass}. Ошибка подключения к базе данных")
    finally:
            if connection:
                            cursor.close()
                            connection.close()
                            logging.info("Команда успешно выполнена")



# region Phone Conversation
def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    logging.info('Thisi start handler')
    return 'findPhoneNumbers'


def findPhoneNumbers (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r"\+?7[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|\+?7[ -]?\d{10}|8[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|8[ -]?\d{10}") # формат 8 (000) 000-00-00
    
    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов
    
    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END# Завершаем выполнение функции
    context.user_data["numbers"] = phoneNumberList
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер
    update.message.reply_text(phoneNumbers)
    update.message.reply_text('Выберите 1, если хотите записать номера в бд. Если нет, отправьте 0.')
    return 'insertPhone' 


def insertPhone (update: Update, context):
    phoneNumberList = context.user_data["numbers"]
    answer = update.message.text
    if answer=='1':
        num_com = ""
        for i in range(len(phoneNumberList)):
            num_com += f"('{phoneNumberList[i]}')"
            num_com += ';' if i == len(phoneNumberList)-1 else ','
        command = f"INSERT INTO Phone(number) VALUES {num_com}"
        db('insert', command)
        update.message.reply_text('Номер записан')
        return ConversationHandler.END
    elif answer=='0':
        update.message.reply_text('Номер не записан')
        return ConversationHandler.END
    else:
        update.message.reply_text('Ответ не распознан. Попробуйте ввести еще раз')
        return 'insertPhone'
# endregion

# region Email Conversation
def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска электронных адресов: ')

    return 'findEmail'

def findEmail (update: Update, context):
    user_input = update.message.text
    emailRegex = re.compile(r"[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+") 
    emailList = emailRegex.findall(user_input) 
    if not emailList: 
        update.message.reply_text('Электронные адреса не найдены')
        return ConversationHandler.END
    context.user_data["emails"] = emailList
    emails = '' 
    for i in range(len(emailList)):
        emails += f'{i+1}. {emailList[i]}\n' 
        
    update.message.reply_text(emails)
    update.message.reply_text('Выберите 1, если хотите записать почту в бд. Если нет, отправьте 0.')
    return 'insertEmail'

def insertEmail(update: Update, context):
    answer = update.message.text
    emailList = context.user_data["emails"]
    if answer == '1':
        num_com = ""
        for i in range(len(emailList)):
            num_com += f"('{emailList[i]}')"
            num_com += ';' if i == len(emailList)-1 else ','
        command = f"INSERT INTO Email (mail) VALUES {num_com}"
        db('insert', command)
        update.message.reply_text('Почта записана')
        return ConversationHandler.END
    elif answer == '0':
        update.message.reply_text('Почта не записана')
        return ConversationHandler.END
    else:
        update.message.reply_text('Ответ не распознан. Попробуйте ввести еще раз')
        return 'insertEmail'
# endregion

# region Verify Password
def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для опредления его сложности: ')
    return 'verifyPassword'

def verifyPassword(update: Update, context):
    user_input = update.message.text
    pwdRegex = re.compile(r"(?=.*[0-9])(?=.*[!@#$%^&*()])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*()]{8,}") 
    pwdResult = pwdRegex.findall(user_input) 
    answer = ""
    if not pwdResult: 
        answer = 'Пароль простой'
    else:
        answer = 'Пароль сложный'
    update.message.reply_text(answer)
    return ConversationHandler.END 
# endregion

# region Linux Info
def getReleaseCommand(update: Update, context):
    command = "lsb_release -a"
    update.message.reply_text(get_system_info(command))

def getUnameCommand(update: Update, context):
    command = "hostnamectl"
    update.message.reply_text(get_system_info(command))

def getUptime(update: Update, context):
    command = "uptime -p"
    update.message.reply_text(get_system_info(command))

def getDf(update: Update, context):
    command = "df -h"
    update.message.reply_text(get_system_info(command))

def getFree(update: Update, context):
    command = "free -h"
    update.message.reply_text(get_system_info(command))

def getMpstat(update: Update, context):
    command = "mpstat"
    update.message.reply_text(get_system_info(command))

def getW(update: Update, context):
    command = "w"
    update.message.reply_text(get_system_info(command))

def getAuths(update: Update, context):
    command = "last -10"
    update.message.reply_text(get_system_info(command))

def getCritical(update: Update, context):
    command = "journalctl -r -p crit -n 5"
    update.message.reply_text(get_system_info(command))

def getPs(update: Update, context):
    command = "ps"
    update.message.reply_text(get_system_info(command)) 

def getSs(update: Update, context):
    command = "ss -lntu"
    update.message.reply_text(get_system_info(command)) 

def getServices(update: Update, context):
    command = "systemctl list-units --type=service | head -n 10"
    update.message.reply_text(get_system_info(command))
# endregion

# Логи реплики

def getReplLogs(update: Update, context):
    data = get_logs()
    result = f"Логи реплики:\n{data}"
    update.message.reply_text(result)

def get_logs():
    message = ""
    try:
        command = "cat /repl_logs/postgresql.log | grep repl | tail -n 15"
        res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0 or res.stderr.decode() != "":
            message = "Файл с логами не открывается"
        else:
            logs = res.stdout.decode().strip('\n')
            message = logs
    except Exception as e:
        message = f"Error: {str(e)}"
    return message

# region Получение информации из БД
def getPhones(update: Update, context):
    command = 'SELECT * FROM Phone;'
    update.message.reply_text(db('select',command))

def getEmails(update: Update, context):
    command = 'SELECT * FROM Email;'
    update.message.reply_text(db('select',command))
# endregion

def getAPTListCommand(update:Update, context):
    update.message.reply_text('Введите название пакета или all, чтобы просмореть информацию о всех пакетах ')
    return 'getAPTList'

def getAPTList(update:Update, context):
    user_input = update.message.text
    command = ""
    if user_input=="all":
        command = "dpkg -l | head -n 15"
    else:
        command = f"dpkg -l {user_input}"
    
    update.message.reply_text(get_system_info(command))
    return ConversationHandler.END 


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'insertPhone': [MessageHandler(Filters.text & ~Filters.command, insertPhone)],
        },
        fallbacks=[]
    )
		
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
            'insertEmail': [MessageHandler(Filters.text & ~Filters.command, insertEmail)],
        },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )

    convHandlerGetAPTList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', getAPTListCommand)],
        states={
            'getAPTList': [MessageHandler(Filters.text & ~Filters.command, getAPTList)],
        },
        fallbacks=[]
    )
	# Регистрируем обработчики команд
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(convHandlerGetAPTList)
    dp.add_handler(CommandHandler("get_release", getReleaseCommand))
    dp.add_handler(CommandHandler("get_uname", getUnameCommand))
    dp.add_handler(CommandHandler("get_uptime", getUptime)) 
    dp.add_handler(CommandHandler("get_df", getDf)) 
    dp.add_handler(CommandHandler("get_free", getFree))
    dp.add_handler(CommandHandler("get_mpstat", getMpstat)) 
    dp.add_handler(CommandHandler("get_w", getW)) 
    dp.add_handler(CommandHandler("get_auths", getAuths))
    dp.add_handler(CommandHandler("get_critical", getCritical)) 
    dp.add_handler(CommandHandler("get_ps", getPs)) 
    dp.add_handler(CommandHandler("get_ss", getSs)) 
    dp.add_handler(CommandHandler("get_services", getServices))
    dp.add_handler(CommandHandler("get_emails", getEmails))
    dp.add_handler(CommandHandler("get_phone_numbers", getPhones)) 
    dp.add_handler(CommandHandler("get_repl_logs", getReplLogs))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
