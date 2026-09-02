import os
import glob
import re

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    # Replace ${amount -> ₹{amount
    content = content.replace('${amount', '₹{amount')
    content = content.replace('${sum(recent)', '₹{sum(recent)')
    content = content.replace('$10,000', '₹10,000')
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

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filepath}")

for root, _, files in os.walk('backend/app'):
    for file in files:
        if file.endswith('.py') or file.endswith('.html'):
            replace_in_file(os.path.join(root, file))

for root, _, files in os.walk('simulator'):
    for file in files:
        if file.endswith('.py'):
            replace_in_file(os.path.join(root, file))

for root, _, files in os.walk('frontend/src'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            replace_in_file(os.path.join(root, file))

print("Replacement complete.")
