import os
import re

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return

    original = content

    # Replace DollarSign icon with IndianRupee icon in TSX/TS files
    if filepath.endswith('.tsx') or filepath.endswith('.ts'):
        content = content.replace('DollarSign', 'IndianRupee')
        content = content.replace('currency = "USD"', 'currency = "INR"')
        content = content.replace("currency = 'USD'", "currency = 'INR'")
        content = content.replace('currency: "USD"', 'currency: "INR"')
        content = content.replace("currency: 'USD'", "currency: 'INR'")
        content = content.replace('dollar savings', 'rupee savings')
        content = content.replace('Dollar Savings', 'Rupee Savings')
        content = content.replace('dollar amount', 'rupee amount')
        content = content.replace('Dollar Amount', 'Rupee Amount')
        content = content.replace('dollar exposure', 'rupee exposure')
        content = content.replace('Dollar Exposure', 'Rupee Exposure')
        content = content.replace('USD', 'INR')

    # Replace in Python files
    if filepath.endswith('.py'):
        content = content.replace('${amount:,.2f}', '₹{amount:,.2f}')
        content = content.replace('${amount:.2f}', '₹{amount:.2f}')
        content = content.replace('${amount}', '₹{amount}')
        content = content.replace('${sum(recent):,.2f}', '₹{sum(recent):,.2f}')
        content = content.replace('$10,000', '₹10,000')
        content = content.replace('$10k', '₹10k')
        content = content.replace('$9,000', '₹9,000')
        content = content.replace('$9,999', '₹9,999')
        content = content.replace('$8,500', '₹8,500')
        content = content.replace('$4,000', '₹4,000')
        content = content.replace('$3,850', '₹3,850')
        content = content.replace('$3,000', '₹3,000')
        content = content.replace('$5,000', '₹5,000')
        content = content.replace('$2,000', '₹2,000')
        content = content.replace('$1,000', '₹1,000')
        content = content.replace('$50,000', '₹50,000')
        content = content.replace('$25,000', '₹25,000')
        content = content.replace('dollar savings', 'rupee savings')
        content = content.replace('Dollar Savings', 'Rupee Savings')
        content = content.replace('dollar amount', 'rupee amount')
        content = content.replace('Dollar Amount', 'Rupee Amount')
        content = content.replace('dollar exposure', 'rupee exposure')
        content = content.replace('Dollar Exposure', 'Rupee Exposure')
        content = content.replace('currency="USD"', 'currency="INR"')
        content = content.replace("currency='USD'", "currency='INR'")
        content = content.replace('"currency": "USD"', '"currency": "INR"')
        content = content.replace("'currency': 'USD'", "'currency': 'INR'")

    # Replace in HTML files
    if filepath.endswith('.html'):
        content = content.replace('$', '₹')
        content = content.replace('USD', 'INR')
        content = content.replace('dollar savings', 'rupee savings')
        content = content.replace('Dollar Savings', 'Rupee Savings')
        content = content.replace('dollar', 'rupee')
        content = content.replace('Dollar', 'Rupee')
        # Revert JS template string ${...} if broken by $ -> ₹ replacement
        content = re.sub(r'₹\{([a-zA-Z0-9_\.\(\)\s\+\-\*\/\,\:\'\"\`\[\]\<\>\=\!\?\&\|]+)\}', r'${\1}', content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filepath}")

for root, _, files in os.walk('frontend/src'):
    for file in files:
        process_file(os.path.join(root, file))

for root, _, files in os.walk('backend/app'):
    for file in files:
        process_file(os.path.join(root, file))

for root, _, files in os.walk('ml_engine'):
    for file in files:
        process_file(os.path.join(root, file))

for root, _, files in os.walk('simulator'):
    for file in files:
        process_file(os.path.join(root, file))

print("All files processed.")
