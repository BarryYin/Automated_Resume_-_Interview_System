import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Optional, List
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # QQ邮箱SMTP配置
        self.smtp_server = "smtp.qq.com"
        self.smtp_port = 465  # SSL端口
        self.sender_email = "1509008060@qq.com"
        self.sender_password = "mvayatiqxmvijeij"  # QQ邮箱授权码
        
    def send_report_email(self, 
                         recipient_email: str, 
                         candidate_name: str,
                         report_content: str,
                         attachment_path: Optional[str] = None) -> bool:
        """
        发送分析报告邮件
        
        Args:
            recipient_email: 收件人邮箱
            candidate_name: 候选人姓名
            report_content: 报告内容
            attachment_path: 附件路径（可选）
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 创建邮件对象
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = f"AI招聘系统 - {candidate_name} 面试分析报告"
            
            # 邮件正文
            body = f"""
尊敬的HR，

您好！

这是AI招聘系统为候选人 {candidate_name} 生成的详细面试分析报告。

报告内容：
{report_content}

本报告基于AI智能分析生成，包含了候选人在以下6个维度的评估：
• 技术能力
• 沟通表达
• 学习能力
• 团队协作
• 问题解决
• 工作态度

如有任何疑问，请随时联系我们。

祝好！
AI招聘系统
            """
            
            # 添加正文到邮件
            message.attach(MIMEText(body, "plain", "utf-8"))
            
            # 添加附件（如果有）
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(attachment_path)}'
                )
                message.attach(part)
            
            # 创建SSL上下文
            context = ssl.create_default_context()
            
            # 连接SMTP服务器并发送邮件
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                text = message.as_string()
                server.sendmail(self.sender_email, recipient_email, text)
            
            logger.info(f"邮件发送成功: {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False
    
    def send_interview_invitation(self, 
                                recipient_email: str, 
                                candidate_name: str,
                                interview_time: str,
                                interview_link: str) -> bool:
        """
        发送面试邀请邮件
        
        Args:
            recipient_email: 收件人邮箱
            candidate_name: 候选人姓名
            interview_time: 面试时间
            interview_link: 面试链接
            
        Returns:
            bool: 发送是否成功
        """
        try:
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = f"面试邀请 - {candidate_name}"
            
            body = f"""
亲爱的 {candidate_name}，

您好！

感谢您对我们公司的关注和申请。经过初步筛选，我们很高兴邀请您参加下一轮面试。

面试详情：
• 面试时间：{interview_time}
• 面试方式：在线面试
• 面试链接：{interview_link}

请您提前5分钟进入面试系统，确保网络连接稳定。面试过程中，我们的AI系统将协助进行技能评估。

如有任何问题，请随时联系我们。

期待与您的交流！

祝好！
HR团队
            """
            
            message.attach(MIMEText(body, "plain", "utf-8"))
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                text = message.as_string()
                server.sendmail(self.sender_email, recipient_email, text)
            
            logger.info(f"面试邀请邮件发送成功: {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"面试邀请邮件发送失败: {str(e)}")
            return False

# 创建全局邮件服务实例
email_service = EmailService()