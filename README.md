# Mookata Ninja (หมูกระทะนินจา)

## สมาชิกในกลุ่ม
1. นางสาวธีริศรา คงลิขิต 6810110164
2. นางสาวภัทรศศิร์ อินทร์นุรักษ์ 6810110252
3. นางสาวนภัทรทสร ณ พัทลุง 6810110474

---

### รายละเอียดโปรเจกต์
เกมแนว Ninja Slash ในธีมหมูกระทะ พัฒนาด้วยภาษา Python และ Kivy Framework

## Overview
**Mookata Ninja** is an action-packed arcade game inspired by the "Ninja Slash" genre, reimagined with a delicious Thai BBQ (Mookata) theme. Players must slice through flying ingredients to score points while avoiding hazardous bombs, all within the vibrant world of a sizzling grill.

## Gameplay Mechanics
The core loop involves slicing ingredients as they are tossed onto the screen.
- **Slicing**: Click and drag your mouse (or swipe on touchscreens) across ingredients.
- **Avoid Bombs**: Slicing a bomb results in an immediate loss of a life.
- **Save Ingredients**: Don't let precious food fall off the bottom of the screen!
## Scoring & Item Types
Different items provide different points and effects:
- **Meat (Normal)**: Basic ingredient, provides standard points.
- **Vegetables**: Healthy choice, provides standard points.
- **Golden Meat**: Rare item that grants bonus points and visual effects.
- **Bomb (Charcoal)**: To be avoided! Slicing these will cost you a life.

## Power-ups & Effects
Special items appear to change the gameplay dynamic:
- **Chili**: Triggers a frenzy mode where ingredients appear faster.
- **Ice**: Slows down the time, making it easier to slice items.
- **Golden Meat**: Rare spawn that significantly boosts your high score.

## Controls & Input
**Mookata Ninja** is designed for intuitive play across devices.
- **Mouse**: Click and drag to create slicing streaks.
- **Touch**: Swipe your finger across the screen to slice.
- **Escape**: Pause the game or return to the main menu.

1. **ระบบตรวจสอบการชน (Collision Detection):** - ตรวจสอบพิกัดการลากเมาส์ (Touch) ว่าตัดผ่านวัตถุ (หมู, ผัก, ถ่าน) บนหน้าจอหรือไม่
   - หากฟันโดนของกิน จะได้คะแนนและเกิดเอฟเฟกต์เสียง (Slash)
   - หากฟันโดนถ่าน (ระเบิด) จะถูกหักหัวใจและเกิดเสียงฉ่า (Sizzle)

2. **ระบบนับคะแนนและคอมโบ (Scoring & Combo System):**
   - อัปเดตคะแนนขึ้นหน้าจอแบบเรียลไทม์
   - มีระบบ Combo หากผู้เล่นฟันโดนของกินต่อเนื่องภายใน 1 วินาที คะแนนที่ได้จะถูกคูณตามจำนวนคอมโบ (เช่น 10, 20, 30...) เพื่อเพิ่มความท้าทาย

3. **ระบบจัดการหัวใจและจบเกม (Health & Game Over Transition):**
   - มีระบบลงโทษ (Penalty) โดยจะหักหัวใจ 1 ดวงเมื่อผู้เล่นปล่อยให้ของกินหล่นทะลุขอบจอด้านล่าง หรือเผลอฟันโดนถ่าน
   - เมื่อหัวใจลดเหลือ 0 ระบบจะหยุดเกม ปิดเพลง BGM และสลับหน้าจอไปยัง `GameOverScreen` ทันที

4. **ระบบบันทึกคะแนนสูงสุด (Save Highscore):**
   - ในหน้า Game Over ผู้เล่นสามารถพิมพ์ชื่อเพื่อบันทึกคะแนนที่เล่นได้
   - ระบบจะเซฟชื่อและคะแนนลงในไฟล์ `highscore.txt` และดึงข้อมูลมาแสดงผลในรอบถัดไป