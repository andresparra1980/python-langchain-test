from typing import List, Dict, Any
from datetime import datetime
from config import config


class NewsletterFormatter:
    """Format research findings into newsletter-style reports"""
    
    @staticmethod
    def format_markdown(
        findings: List[Dict[str, Any]],
        title: str = None,
        introduction: str = None
    ) -> str:
        """
        Format findings as Markdown newsletter.
        
        Args:
            findings: List of research findings, each with keys: topic, summary, sources, tags
            title: Newsletter title (optional)
            introduction: Introduction text (optional)
            
        Returns:
            Formatted Markdown string
        """
        date_str = datetime.now().strftime("%B %d, %Y")
        title = title or f"AI Research Digest - {date_str}"
        
        output = f"# {title}\n\n"
        output += f"*Generated on {date_str}*\n\n"
        
        if introduction:
            output += f"{introduction}\n\n"
        
        output += "---\n\n"
        
        if not findings:
            output += "No new findings to report.\n"
            return output
        
        output += f"## Key Findings ({len(findings)} topics)\n\n"
        
        for i, finding in enumerate(findings, 1):
            topic = finding.get("topic", "Untitled")
            summary = finding.get("summary", "No summary available")
            sources = finding.get("sources", [])
            tags = finding.get("tags", [])
            
            output += f"### {i}. {topic}\n\n"
            output += f"{summary}\n\n"
            
            if tags:
                output += f"**Tags:** {', '.join(tags)}\n\n"
            
            if sources:
                output += "**Sources:**\n"
                for source in sources[:5]:  # Limit to 5 sources
                    output += f"- {source}\n"
                if len(sources) > 5:
                    output += f"- *...and {len(sources) - 5} more*\n"
                output += "\n"
            
            output += "---\n\n"
        
        # Footer
        output += "*This newsletter was generated automatically by the AI Research Assistant.*\n"
        
        return output
    
    @staticmethod
    def format_html(
        findings: List[Dict[str, Any]],
        title: str = None,
        introduction: str = None
    ) -> str:
        """
        Format findings as HTML newsletter.
        
        Args:
            findings: List of research findings
            title: Newsletter title (optional)
            introduction: Introduction text (optional)
            
        Returns:
            Formatted HTML string
        """
        date_str = datetime.now().strftime("%B %d, %Y")
        title = title or f"AI Research Digest - {date_str}"
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2c3e50;
            margin-top: 30px;
        }}
        h3 {{
            color: #34495e;
            margin-top: 25px;
        }}
        .date {{
            color: #7f8c8d;
            font-style: italic;
            margin-bottom: 20px;
        }}
        .introduction {{
            background-color: #ecf0f1;
            padding: 15px;
            border-left: 4px solid #3498db;
            margin: 20px 0;
        }}
        .finding {{
            border-left: 3px solid #3498db;
            padding-left: 20px;
            margin: 25px 0;
        }}
        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 10px 0;
        }}
        .tag {{
            background-color: #3498db;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
        }}
        .sources {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
        }}
        .sources ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .sources li {{
            margin: 8px 0;
        }}
        .sources a {{
            color: #3498db;
            text-decoration: none;
        }}
        .sources a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: center;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ecf0f1;
            margin: 30px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p class="date">Generated on {date_str}</p>
"""
        
        if introduction:
            html += f"""
        <div class="introduction">
            <p>{introduction}</p>
        </div>
"""
        
        if not findings:
            html += """
        <p>No new findings to report.</p>
"""
        else:
            html += f"""
        <h2>Key Findings ({len(findings)} topics)</h2>
"""
            
            for i, finding in enumerate(findings, 1):
                topic = finding.get("topic", "Untitled")
                summary = finding.get("summary", "No summary available")
                sources = finding.get("sources", [])
                tags = finding.get("tags", [])
                
                html += f"""
        <div class="finding">
            <h3>{i}. {topic}</h3>
            <p>{summary}</p>
"""
                
                if tags:
                    html += """
            <div class="tags">
"""
                    for tag in tags:
                        html += f"""
                <span class="tag">{tag}</span>
"""
                    html += """
            </div>
"""
                
                if sources:
                    html += """
            <div class="sources">
                <strong>Sources:</strong>
                <ul>
"""
                    for source in sources[:5]:
                        html += f"""
                    <li><a href="{source}" target="_blank">{source}</a></li>
"""
                    if len(sources) > 5:
                        html += f"""
                    <li><em>...and {len(sources) - 5} more</em></li>
"""
                    html += """
                </ul>
            </div>
"""
                
                if i < len(findings):
                    html += """
            <hr>
"""
                
                html += """
        </div>
"""
        
        html += """
        <div class="footer">
            <p>This newsletter was generated automatically by the AI Research Assistant.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    @staticmethod
    def format_plain_text(
        findings: List[Dict[str, Any]],
        title: str = None,
        introduction: str = None
    ) -> str:
        """
        Format findings as plain text newsletter.
        
        Args:
            findings: List of research findings
            title: Newsletter title (optional)
            introduction: Introduction text (optional)
            
        Returns:
            Formatted plain text string
        """
        date_str = datetime.now().strftime("%B %d, %Y")
        title = title or f"AI Research Digest - {date_str}"
        
        output = f"{title}\n"
        output += "=" * len(title) + "\n\n"
        output += f"Generated on {date_str}\n\n"
        
        if introduction:
            output += f"{introduction}\n\n"
        
        output += "-" * 70 + "\n\n"
        
        if not findings:
            output += "No new findings to report.\n"
            return output
        
        output += f"KEY FINDINGS ({len(findings)} topics)\n\n"
        
        for i, finding in enumerate(findings, 1):
            topic = finding.get("topic", "Untitled")
            summary = finding.get("summary", "No summary available")
            sources = finding.get("sources", [])
            tags = finding.get("tags", [])
            
            output += f"{i}. {topic.upper()}\n\n"
            output += f"   {summary}\n\n"
            
            if tags:
                output += f"   Tags: {', '.join(tags)}\n\n"
            
            if sources:
                output += "   Sources:\n"
                for source in sources[:5]:
                    output += f"   - {source}\n"
                if len(sources) > 5:
                    output += f"   - ...and {len(sources) - 5} more\n"
                output += "\n"
            
            output += "-" * 70 + "\n\n"
        
        output += "\nThis newsletter was generated automatically by the AI Research Assistant.\n"
        
        return output


def format_newsletter(
    findings: List[Dict[str, Any]],
    format_type: str = "html",
    title: str = None,
    introduction: str = None
) -> str:
    """
    Convenience function to format newsletter in specified format.
    
    Args:
        findings: List of research findings
        format_type: Format type ('html', 'markdown', or 'text')
        title: Newsletter title
        introduction: Introduction text
        
    Returns:
        Formatted newsletter string
    """
    formatter = NewsletterFormatter()
    
    format_type = format_type.lower()
    
    if format_type == "html":
        return formatter.format_html(findings, title, introduction)
    elif format_type == "markdown":
        return formatter.format_markdown(findings, title, introduction)
    elif format_type in ("text", "plain"):
        return formatter.format_plain_text(findings, title, introduction)
    else:
        raise ValueError(f"Unknown format type: {format_type}")
