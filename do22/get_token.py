import asyncio
from pyppeteer import launch
import logging
import re
from typing import Optional
import random
import os

class MacTokenScraper:
    def __init__(self):
        self._setup_logging()
        self._setup_config()

    def _setup_logging(self):
        """配置日志系统"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _setup_config(self):
        """初始化配置"""
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        ]
        
        # 增强的反检测脚本
        self.stealth_js = '''
        () => {
            Object.defineProperties(navigator, {
                webdriver: { get: () => undefined },
                platform: { get: () => 'MacIntel' },
                languages: { get: () => ['zh-CN', 'zh'] }
            });
            
            window.navigator.chrome = { runtime: {} };
            
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = parameters => (
                parameters.name === 'notifications' 
                ? Promise.resolve({state: Notification.permission}) 
                : originalQuery(parameters)
            );
        }
        '''

    async def _setup_browser(self):
        """配置并启动浏览器"""
        try:
            return await launch({
                'headless': True,
                'args': [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--window-size=1440,900',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ],
                'ignoreHTTPSErrors': True,
                'defaultViewport': {
                    'width': 1440,
                    'height': 900,
                    'deviceScaleFactor': 2
                }
            })
        except Exception as e:
            self.logger.error(f"浏览器启动失败: {e}")
            return None

    async def _extract_token(self, page):
        """增强的token提取逻辑"""
        return await page.evaluate('''
            () => {
                let token = null;
                try {
                    const scriptContent = Array.from(document.getElementsByTagName('script'))
                        .map(script => script.textContent)
                        .find(content => content.includes('let token ='));
                    if (scriptContent) {
                        const match = scriptContent.match(/let token = "([^"]+)"/);
                        if (match) token = match[1];
                    }
                } catch (error) {
                    console.error("Token提取错误:", error);
                }
                return token;
            }
        ''')

    async def get_token(self, max_retries: int = 3) -> Optional[str]:
        """获取token的主方法"""
        for attempt in range(max_retries):
            browser = None
            try:
                self.logger.info(f"开始第 {attempt + 1} 次尝试")
                
                browser = await self._setup_browser()
                if not browser:
                    continue
                    
                page = await browser.newPage()
                await page.setUserAgent(random.choice(self.user_agents))
                await page.evaluateOnNewDocument(self.stealth_js)
                
                # 访问页面
                self.logger.info("访问目标页面")
                await page.goto('https://22.do/', {
                    'waitUntil': 'domcontentloaded',
                    'timeout': 30000
                })
                
                # 等待并点击按钮
                await page.waitForSelector('#into-mailbox', {
                    'visible': True,
                    'timeout': 30000
                })
                
                await asyncio.sleep(random.uniform(1, 2))
                await page.click('#into-mailbox')
                
                # 等待页面跳转
                await page.waitForNavigation({
                    'waitUntil': 'domcontentloaded',
                    'timeout': 30000
                })
                
                # 提取token
                token = await self._extract_token(page)
                
                if token:
                    self.logger.info(f"成功获取token: {token}")
                    return token
                
                self.logger.warning("未找到token")
                
            except Exception as e:
                self.logger.error(f"错误: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(random.uniform(2, 4))
            finally:
                if browser:
                    await browser.close()
        
        return None

async def main():
    """主函数"""
    try:
        scraper = MacTokenScraper()
        token = await scraper.get_token()
        if token:
            print(f"成功获取token: {token}")
        else:
            print("获取token失败")
    except Exception as e:
        print(f"程序执行出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
