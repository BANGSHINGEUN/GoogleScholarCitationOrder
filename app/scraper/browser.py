import time
import random
import os
import subprocess
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from fake_useragent import UserAgent

from app.core.config import settings
from app.core.logging import logger

# 다양한 일반적인 User-Agent 리스트 (fake_useragent 라이브러리가 실패할 경우를 대비)
COMMON_USER_AGENTS = [
    # Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    # Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

class BrowserManager:
    """Selenium 브라우저 관리 클래스"""
    
    def __init__(self):
        self.browser = None
        try:
            self.user_agent = UserAgent() if settings.USER_AGENT_ROTATION else None
        except Exception as e:
            logger.warning(f"User-Agent 생성 오류: {str(e)}. 기본 User-Agent 목록을 사용합니다.")
            self.user_agent = None
    
    def get_browser(self):
        """설정된 옵션에 따라 Selenium 브라우저 인스턴스 반환"""
        if self.browser is not None:
            return self.browser
        
        if settings.BROWSER_TYPE.lower() == "chrome":
            self.browser = self._setup_chrome()
        else:
            raise ValueError(f"지원되지 않는 브라우저 유형: {settings.BROWSER_TYPE}")
        
        return self.browser
    
    def _find_chromedriver(self):
        """시스템에 맞는 ChromeDriver 찾기 (macOS용 대체 메서드)"""
        # Docker 환경의 Chromium/ChromeDriver 경로 확인
        if os.environ.get('CHROMEDRIVER_PATH'):
            return os.environ.get('CHROMEDRIVER_PATH')
            
        # Mac에서 brew로 설치된 chromedriver 확인
        try:
            result = subprocess.run(['which', 'chromedriver'], 
                                   capture_output=True, text=True, check=False)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"which chromedriver 실행 중 오류: {str(e)}")
        
        # 일반적인 설치 경로 확인
        common_paths = [
            "/usr/local/bin/chromedriver",
            "/usr/bin/chromedriver",
            os.path.expanduser("~/chromedriver")
        ]
        
        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
                
        return None
    
    def _setup_chrome(self):
        """Chrome 브라우저 설정"""
        options = Options()
        
        # 헤드리스 모드 설정
        if settings.HEADLESS:
            options.add_argument("--headless")
        
        # 기본 옵션 설정
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # Docker 환경에서 Chromium 사용 설정
        if os.environ.get('CHROME_BIN'):
            options.binary_location = os.environ.get('CHROME_BIN')
            logger.debug(f"Docker 환경에서 Chromium 사용: {options.binary_location}")
        
        # User-Agent 설정
        if self.user_agent:
            try:
                user_agent_str = self.user_agent.random
                options.add_argument(f"--user-agent={user_agent_str}")
                logger.debug(f"User-Agent 설정: {user_agent_str}")
            except Exception as e:
                logger.warning(f"User-Agent 설정 오류: {str(e)}. 랜덤 기본 User-Agent를 사용합니다.")
                random_ua = random.choice(COMMON_USER_AGENTS)
                options.add_argument(f"--user-agent={random_ua}")
                logger.debug(f"기본 User-Agent 설정: {random_ua}")
        
        # 구글 봇 감지 회피를 위한 추가 설정
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # 웹사이트가 자동화 감지하지 못하도록 navigator.webdriver 플래그 수정
        options.add_argument("--disable-blink-features")
        
        # 기타 보안 설정
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        
        # 로그 레벨 설정
        if settings.LOG_LEVEL.upper() != "DEBUG":
            options.add_argument("--log-level=3")  # 불필요한 로그 숨김
        
        # 시스템에 맞는 ChromeDriver 설정
        try:
            driver_path = None
            
            # Docker 환경에서 ChromeDriver 경로 확인
            if os.environ.get('CHROMEDRIVER_PATH'):
                driver_path = os.environ.get('CHROMEDRIVER_PATH')
                logger.debug(f"Docker 환경의 ChromeDriver 사용: {driver_path}")
            else:
                # Mac ARM(M1/M2) 환경 확인
                is_mac_arm = platform.system() == 'Darwin' and platform.machine().startswith('arm')
                
                # 기본 방법으로 시도 
                try:
                    if is_mac_arm:
                        logger.debug("Mac ARM 아키텍처 감지, 적절한 ChromeDriver 선택")
                        driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
                    else:
                        driver_path = ChromeDriverManager().install()
                except Exception as e:
                    logger.warning(f"ChromeDriverManager 오류: {str(e)}")
                    
                # 기본 방법 실패한 경우 대체 방법 시도
                if not driver_path or not os.path.exists(driver_path):
                    logger.debug("대체 방법으로 ChromeDriver 찾기 시도")
                    driver_path = self._find_chromedriver()
                
            if not driver_path:
                raise ValueError("ChromeDriver를 찾을 수 없습니다. brew install chromedriver 또는 apt-get install chromium-driver로 설치해 주세요.")
                
            logger.debug(f"ChromeDriver 경로: {driver_path}")
            
            # ChromeDriver 서비스 생성 및 브라우저 인스턴스 생성
            service = Service(executable_path=driver_path)
            browser = webdriver.Chrome(service=service, options=options)
            
            # navigator.webdriver를 숨기기 위한 JavaScript 실행
            browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            logger.debug("Chrome 브라우저 인스턴스 생성 완료")
            return browser
        except Exception as e:
            logger.error(f"Chrome 브라우저 설정 중 오류 발생: {str(e)}")
            raise
    
    def close(self):
        """브라우저 인스턴스 종료"""
        if self.browser:
            try:
                self.browser.quit()
                logger.debug("브라우저 인스턴스 종료 완료")
            except Exception as e:
                logger.error(f"브라우저 종료 중 오류 발생: {str(e)}")
            finally:
                self.browser = None
    
    def rotate_user_agent(self):
        """User-Agent 변경"""
        if not self.browser:
            return
        
        try:
            if self.user_agent:
                new_user_agent = self.user_agent.random
            else:
                new_user_agent = random.choice(COMMON_USER_AGENTS)
                
            self.browser.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": new_user_agent})
            logger.debug(f"User-Agent 변경: {new_user_agent}")
        except Exception as e:
            logger.warning(f"User-Agent 변경 오류: {str(e)}")
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        """랜덤한 지연 시간 추가 (IP 차단 방지)"""
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"랜덤 지연 적용: {delay:.2f}초")
        time.sleep(delay)
        

# 싱글톤 인스턴스
browser_manager = BrowserManager() 