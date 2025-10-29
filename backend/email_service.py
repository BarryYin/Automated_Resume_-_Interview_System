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
    
    def send_custom_interview_invitation(self, 
                                       recipient_email: str, 
                                       candidate_name: str,
                                       subject: str,
                                       interview_time: str,
                                       content: str,
                                       interview_link: str) -> bool:
        """
        发送自定义内容的面试邀请邮件
        
        Args:
            recipient_email: 收件人邮箱
            candidate_name: 候选人姓名
            subject: 邮件主题
            interview_time: 面试时间
            content: 自定义邮件内容
            interview_link: 面试链接
            
        Returns:
            bool: 发送是否成功
        """
        try:
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            
            # 替换内容中的占位符
            formatted_content = content.replace('[面试链接将自动生成]', interview_link)
            formatted_content = formatted_content.replace('[面试时间]', interview_time)
            formatted_content = formatted_content.replace('[候选人姓名]', candidate_name)
            
            # 添加面试链接信息
            body = f"""
{formatted_content}

面试详情：
• 面试时间：{interview_time}
• 面试链接：{interview_link}

请点击上方链接或复制到浏览器中打开进行面试。

祝好！
HR团队
            """
            
            message.attach(MIMEText(body, "plain", "utf-8"))
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                text = message.as_string()
                server.sendmail(self.sender_email, recipient_email, text)
            
            logger.info(f"自定义面试邀请邮件发送成功: {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"自定义面试邀请邮件发送失败: {str(e)}")
            return False
    
    def send_status_notification(self, 
                               recipient_email: str, 
                               candidate_name: str,
                               status: str) -> bool:
        """
        发送状态通知邮件
        
        Args:
            recipient_email: 收件人邮箱
            candidate_name: 候选人姓名
            status: 新状态
            
        Returns:
            bool: 发送是否成功
        """
        try:
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # 根据状态设置不同的邮件内容
            status_configs = {
                '进入复试': {
                    'subject': '恭喜！您已通过初试',
                    'content': f"""
亲爱的 {candidate_name}，

恭喜您！

经过我们的综合评估，您在初试中表现优秀，我们很高兴地通知您已通过初试阶段。

接下来，我们诚挚邀请您参加复试环节。复试将更深入地了解您的专业能力和团队协作精神。

我们的HR同事会在近期与您联系，安排具体的复试时间和形式。

再次恭喜您取得的优异表现！

祝好！
HR团队
                    """
                },
                '录取试用': {
                    'subject': '🎉 录取通知 - 欢迎加入我们！',
                    'content': f"""
亲爱的 {candidate_name}，

恭喜您！🎉

经过全面的评估和考虑，我们很高兴地通知您：您已被我们公司录取为试用员工！

您的专业能力、工作态度和团队协作精神都给我们留下了深刻的印象。我们相信您将为团队带来新的活力和价值。

接下来的步骤：
• 我们的HR同事会与您联系，讨论入职相关事宜
• 请准备好相关的入职材料
• 试用期为3个月，期间我们会提供全面的培训和支持

我们期待您的加入，共同创造美好的未来！

热烈欢迎！
HR团队
                    """
                },
                '不匹配': {
                    'subject': '面试结果通知',
                    'content': f"""
亲爱的 {candidate_name}，

感谢您参与我们公司的面试流程。

经过慎重的考虑和评估，我们认为您的背景和经验与当前职位的要求暂时不太匹配。这个决定并不容易做出，因为我们看到了您的许多优秀品质。

请不要因此感到沮丧。每个人都有自己独特的优势和适合的发展道路。我们相信您一定能找到更适合发挥您才能的机会。

如果未来有更合适的职位机会，我们会很乐意再次考虑您的申请。

感谢您对我们公司的关注，祝您前程似锦！

祝好！
HR团队
                    """
                }
            }
            
            config = status_configs.get(status, {
                'subject': f'面试状态更新 - {status}',
                'content': f"""
亲爱的 {candidate_name}，

您好！

您的面试状态已更新为：{status}

如有任何疑问，请随时联系我们。

祝好！
HR团队
                """
            })
            
            message["Subject"] = config['subject']
            message.attach(MIMEText(config['content'], "plain", "utf-8"))
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                text = message.as_string()
                server.sendmail(self.sender_email, recipient_email, text)
            
            logger.info(f"状态通知邮件发送成功: {recipient_email} - {status}")
            return True
            
        except Exception as e:
            logger.error(f"状态通知邮件发送失败: {str(e)}")
            return False

# 创建全局邮件服务实例
email_service = EmailService()