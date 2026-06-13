import requests
import json

print('=== 体积收缩校正功能测试 ===')
print()

print('1. 不启用收缩校正 (默认):')
resp = requests.post('http://127.0.0.1:5000/calculate',
    json={'mother_concentration': 100, 'target_concentration': 50, 'mother_volume': 500})
r = resp.json()['result']
print(f'   理论溶剂体积: {r["solvent_volume"]} ml')
print(f'   理论最终体积: {r["final_volume"]} ml')
print(f'   收缩校正: {r["contraction_corrected"]}')
print()

print('2. 启用自动收缩校正 (50% ABV, 收缩率最大):')
resp = requests.post('http://127.0.0.1:5000/calculate',
    json={'mother_concentration': 100, 'target_concentration': 50, 'mother_volume': 500,
          'correct_contraction': True})
r = resp.json()['result']
print(f'   理论溶剂体积: {r["solvent_volume"]} ml')
print(f'   校正后溶剂体积: {r["corrected_solvent_volume"]} ml')
extra_pct = r["volume_difference"] / r["solvent_volume"] * 100
print(f'   体积差值: {r["volume_difference"]} ml (多加入 {extra_pct:.2f}%)')
print(f'   收缩率: {r["contraction_rate"]}%')
print(f'   校正后最终体积: {r["corrected_final_volume"]} ml')
print()

print('3. 70%酒精稀释 (70%消毒酒精):')
resp = requests.post('http://127.0.0.1:5000/calculate',
    json={'mother_concentration': 95, 'target_concentration': 70, 'mother_volume': 1000,
          'correct_contraction': True, 'temperature': 25.0})
r = resp.json()['result']
print(f'   理论溶剂体积: {r["solvent_volume"]} ml')
print(f'   校正后溶剂体积: {r["corrected_solvent_volume"]} ml')
print(f'   体积差值: {r["volume_difference"]} ml')
print(f'   收缩率: {r["contraction_rate"]}% (25°C)')
print()

print('4. 使用手动收缩率 (3%):')
resp = requests.post('http://127.0.0.1:5000/calculate',
    json={'mother_concentration': 100, 'target_concentration': 60, 'mother_volume': 600,
          'correct_contraction': True, 'manual_contraction_rate': 3.0})
r = resp.json()['result']
print(f'   理论溶剂体积: {r["solvent_volume"]} ml')
print(f'   校正后溶剂体积: {r["corrected_solvent_volume"]} ml')
print(f'   体积差值: {r["volume_difference"]} ml')
print(f'   手动收缩率: {r["contraction_rate"]}%')
print()

print('5. 对比 - 配50%酒精1000ml需要多少95%酒精:')
print('   常规计算: 1000 * 50 / 95 = 526.32 ml 95%酒精 + 473.68 ml 水')
print('   但实际混合后体积收缩，需要调整...')
resp = requests.post('http://127.0.0.1:5000/calculate',
    json={'mother_concentration': 95, 'target_concentration': 50, 'mother_volume': 526.32,
          'correct_contraction': True})
r = resp.json()['result']
print(f'   校正后需要加水: {r["corrected_solvent_volume"]} ml')
print(f'   比理论多加: {r["volume_difference"]} ml')
print(f'   最终体积: {r["corrected_final_volume"]} ml')
print()

print('=== Bug 修复效果总结 ===')
print('50% ABV时体积收缩约3.2%，意味着:')
print('- 500ml 100%酒精 + 500ml水 = 理论1000ml，实际只有约968ml')
print('- 要得到1000ml 50%酒精，需要多加入约33ml水')
print('- 这就是之前浓度计算误差的来源！')
