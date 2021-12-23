from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import random
import pickle
import logging
import os
import json



COOKIE_FILE = "cookies.pkl"
driver = webdriver.Chrome('chromedriver.exe')


def read_config():
    with open('config.json') as json_file:
        config = json.load(json_file)
        userdata = config['userdata']
        log_level = config['log_level']
        comment_list = config['comment_list']
        post_list = config['post_list']
        block_limit = config['block_limit']

    logger.debug("configs loaded")
    
    return userdata, log_level, comment_list, post_list, block_limit
        

def get_logger(log_level):
    logger = logging.getLogger(__name__)
    file = logging.FileHandler("logs/comments.log")
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', "%Y-%m-%d %H:%M:%S")
    file.setFormatter(formatter)
    logger.addHandler(file)

    if log_level == "debug":
        logger.setLevel(logging.DEBUG)
    elif log_level == "info":
        logger.setLevel(logging.INFO)
    elif log_level == "warning":
        logger.setLevel(logging.WARNING)
    elif log_level == "error":
        logger.setLevel(logging.ERROR)
    else:
        print("log_level must be: debug, info, warning or error")
        exit()

    return logger


def login(userdata):
    base_url = "https://www.instagram.com"
    try:
        driver.get(base_url)
        logger.debug("loading old cookies")
        cookies = pickle.load(open(COOKIE_FILE, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.get(base_url)
        logger.debug("cookies loaded ")
        
    except:
        logger.warning("could not load cookies")
        logger.debug("starting new session")
        driver.get(base_url)

        sleep_time = random.uniform(2.0, 3.0)
        sleep(sleep_time)

        try:
            driver.find_element_by_xpath("/html/body/div[4]/div/div/button[1]").click()
            logger.debug("accepted cookie usage")
        except:
            pass

        sleep_time = random.uniform(5.0, 7.0)
        sleep(sleep_time)

        username = driver.find_element_by_xpath("/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[1]/div/label/input")
        password = driver.find_element_by_xpath("/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[2]/div/label/input")
        username.send_keys(userdata['username'])
        password.send_keys(userdata['password'])
        logger.debug("userdata entered")

        sleep_time = random.uniform(3.0, 5.0)
        sleep(sleep_time)

        driver.find_element_by_xpath("/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[3]/button/div").click()

        sleep_time = random.uniform(3.0, 5.0)
        sleep(sleep_time)

        try:
            driver.find_element_by_class_name("Rt8TI")
            logger.error(f"login failed")
            return False
        except:
            pass

        try:
            driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div/div/div/button").click()
        except:
            pass
        
        sleep_time = random.uniform(3.0, 5.0)
        sleep(sleep_time)

        try:
            driver.find_element_by_xpath("/html/body/div[5]/div/div/div/div[3]/button[2]").click()
        except:
            pass
        
        logger.debug("new session started successfully")
        sleep_time = random.uniform(1.0, 2.0)
        sleep(sleep_time)

        pickle.dump( driver.get_cookies() , open(COOKIE_FILE,"wb"))
        logger.info("new cookies saved")

    return True


def comment(url, comment_list):
    logger.debug(f"starting round on {url}")
    driver.get(url)

    sleep_time = random.uniform(1.0, 3.0)
    sleep(sleep_time)

    for i in range(5):
        driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div[1]/article/div/div[2]/div/div[2]/section[3]/div/form/textarea").click()    
        action = ActionChains(driver)
        comment = comment_list[random.randint(0, len(comment_list) - 1)]
        action.send_keys(comment)
        action.perform()

        logger.debug(f"comment test \"{comment}\" on {url}")
        
        sleep_time = random.uniform(3.0, 5.0)
        sleep(sleep_time)

        driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div[1]/article/div/div[2]/div/div[2]/section[3]/div/form/button[2]").click()
        logger.debug(f"sending comment on {url}")

        sleep_time = 2.0
        sleep(sleep_time)

        try:
            driver.find_element_by_class_name("gxNyb")
            logger.error(f"failed to send comment on {url}")
            driver.find_element_by_xpath("/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[6]/span/img").click()
            driver.find_element_by_xpath("/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[6]/div[2]/div[2]/div[2]/div[2]/div/div/div/div/div/div").click()
            logger.debug("current session stopped")
            os.remove(COOKIE_FILE)
            logger.debug("old cookies removed")

            return False
        except:
            pass

        logger.info(f"comment sent on {url}")

        sleep_time = random.uniform(10.0, 15.0)
        sleep(sleep_time)

    return True


if __name__ == "__main__":

    userdata, log_level, comment_list, post_list, block_limit = read_config()

    logger = get_logger(log_level)

    for i in range(block_limit):
        if not login(userdata):
            sleep_time = random.uniform(600.0, 900.0)
            logger.debug(f"waiting {round(sleep_time, 1)}s")
            sleep(sleep_time)
            continue

        while True:
            if not comment(post_list[random.randint(0, len(post_list) - 1)], comment_list):
                break
            if not comment(post_list[random.randint(0, len(post_list) - 1)], comment_list):
                break
            
            sleep_time = random.uniform(300.0, 400.0)
            logger.debug(f"waiting {round(sleep_time, 1)}s")
            sleep(sleep_time)

        sleep_time = random.uniform(400.0, 500.0)
        logger.debug(f"waiting {round(sleep_time, 1)}s")
        sleep(sleep_time)
    
    logger.critical(f"blocklimit reached")