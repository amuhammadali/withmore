with open('frontend/src/miniapp/MiniApp.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove fitting state in ProductScreen
start_state = '  // Fitting appointment state'
end_state = '  useEffect(() => {\n    shopFetch("/api/shop/reviews")'
if start_state in text and end_state in text:
    p1 = text.find(start_state)
    p2 = text.find(end_state)
    text = text[:p1] + text[p2:]
    print('Fitting state removed')

# Remove fitting modal in ProductScreen
start_modal = '{/* Atelier Fitting Appointment Modal */}'
end_modal = '{/* Quick Order Modal */}'
if start_modal in text and end_modal in text:
    p1 = text.find(start_modal)
    p2 = text.find(end_modal)
    text = text[:p1] + text[p2:]
    print('Fitting modal removed')

with open('frontend/src/miniapp/MiniApp.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done cleaning MiniApp.tsx')

