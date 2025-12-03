"""
Slack Helper - Handles Slack notifications for sprint events
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SlackNotifier:
    def __init__(self):
        self.enabled = os.getenv("SLACK_ENABLED", "false").lower() == "true"
        self.bot_token = os.getenv("SLACK_BOT_TOKEN", "")
        self.channel_id = os.getenv("SLACK_CHANNEL_ID", "")
        
        self.client = None
        
        if self.enabled and self.bot_token and self.channel_id:
            try:
                from slack_sdk import WebClient
                self.client = WebClient(token=self.bot_token)
                print("[Slack] Initialized successfully")
            except ImportError:
                print("[Slack Error] slack-sdk not installed. Run: pip install slack-sdk")
                self.enabled = False
            except Exception as e:
                print(f"[Slack Error] Failed to initialize: {e}")
                self.enabled = False
        else:
            print("[Slack] Disabled or not configured")
    
    def is_enabled(self):
        """Check if Slack notifications are enabled and configured"""
        return self.enabled and self.client is not None
    
    def send_message(self, message: str, title: str = None):
        """
        Send a simple text message to Slack
        
        Args:
            message: Message text
            title: Optional title/header
        """
        if not self.is_enabled():
            return False
        
        try:
            blocks = []
            
            if title:
                blocks.append({
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": title
                    }
                })
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            })
            
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=blocks,
                text=message  # Fallback text
            )
            
            return response["ok"]
        except Exception as e:
            print(f"[Slack Error] Failed to send message: {e}")
            return False
    
    def send_standup_summary(self, sprint_number: int, summary: str, blockers: list):
        """
        Send daily standup summary notification
        
        Args:
            sprint_number: Sprint number
            summary: Standup summary text
            blockers: List of blocker strings
        """
        if not self.is_enabled():
            return False
        
        try:
            # Format blockers
            blockers_text = "\n".join([f"• {blocker}" for blocker in blockers]) if blockers else "None reported"
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📊 Sprint {sprint_number} Daily Standup"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Summary:*\n{summary}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Blockers:*\n{blockers_text}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "Daily standup completed successfully!"
                        }
                    ]
                }
            ]
            
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=blocks,
                text=f"Sprint {sprint_number} Daily Standup Summary"
            )
            
            return response["ok"]
        except Exception as e:
            print(f"[Slack Error] Failed to send standup summary: {e}")
            return False
    
    def send_planning_complete(self, sprint_number: int, total_points: int, story_count: int):
        """
        Send sprint planning completion notification
        
        Args:
            sprint_number: Sprint number
            total_points: Total story points planned
            story_count: Number of stories in sprint
        """
        if not self.is_enabled():
            return False
        
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"✅ Sprint {sprint_number} Planning Complete"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Points:*\n{total_points}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Story Count:*\n{story_count}"
                        }
                    ]
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "Sprint planning has been approved and the sprint is ready to start!"
                        }
                    ]
                }
            ]
            
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=blocks,
                text=f"Sprint {sprint_number} Planning Complete - {story_count} stories, {total_points} points"
            )
            
            return response["ok"]
        except Exception as e:
            print(f"[Slack Error] Failed to send planning notification: {e}")
            return False
    
    def send_retrospective_summary(self, sprint_number: int, went_well: list, needs_improvement: list):
        """
        Send retrospective summary notification
        
        Args:
            sprint_number: Sprint number
            went_well: List of things that went well (strings)
            needs_improvement: List of things that need improvement (strings)
        """
        if not self.is_enabled():
            return False
        
        try:
            # Format went well items (limit to top 5)
            went_well_text = "\n".join([f"• {item}" for item in went_well[:5]]) if went_well else "No items provided"
            
            # Format needs improvement items (limit to top 5)
            needs_improvement_text = "\n".join([f"• {item}" for item in needs_improvement[:5]]) if needs_improvement else "No items provided"
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🔄 Sprint {sprint_number} Retrospective Summary"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*What Went Well:*\n{went_well_text}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Needs Improvement:*\n{needs_improvement_text}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "Review the full retrospective and action items in the system."
                        }
                    ]
                }
            ]
            
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=blocks,
                text=f"Sprint {sprint_number} Retrospective Summary"
            )
            
            return response["ok"]
        except Exception as e:
            print(f"[Slack Error] Failed to send retrospective summary: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_action_items_created(self, sprint_number: int, action_items: list):
        """
        Send action items created notification
        
        Args:
            sprint_number: Sprint number
            action_items: List of dicts with keys: action_id, title, assigned_to, priority
        """
        if not self.is_enabled():
            return False
        
        try:
            # Format action items (limit to top 10)
            items_text = ""
            for item in action_items[:10]:
                items_text += f"• *{item['action_id']}*: {item['title']}\n"
                items_text += f"  _Assigned: {item['assigned_to']} | Priority: {item['priority']}_\n\n"
            
            if not items_text:
                items_text = "No action items created"
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🎯 Sprint {sprint_number} Action Items Created"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{len(action_items)} action items have been created:*\n\n{items_text}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "Action items from retrospective have been assigned to team members."
                        }
                    ]
                }
            ]
            
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=blocks,
                text=f"Sprint {sprint_number} - {len(action_items)} action items created"
            )
            
            return response["ok"]
        except Exception as e:
            print(f"[Slack Error] Failed to send action items notification: {e}")
            import traceback
            traceback.print_exc()
            return False


# Test the Slack integration
if __name__ == "__main__":
    print("Testing Slack Integration...")
    print("=" * 60)
    
    slack = SlackNotifier()
    
    print(f"Slack Enabled: {slack.is_enabled()}")
    print(f"Bot Token: {'Set' if slack.bot_token else 'Not Set'}")
    print(f"Channel ID: {slack.channel_id if slack.channel_id else 'Not Set'}")
    
    if slack.is_enabled():
        print("\nSending test message...")
        result = slack.send_message(
            "This is a test message from the Agile Sprint Assistant!",
            "🤖 Test Notification"
        )
        print(f"Test message sent: {result}")
    else:
        print("\nSlack is not enabled or not properly configured.")
        print("To enable Slack notifications:")
        print("1. Set SLACK_ENABLED=true in your .env file")
        print("2. Add your SLACK_BOT_TOKEN (starts with xoxb-)")
        print("3. Add your SLACK_CHANNEL_ID (starts with C)")