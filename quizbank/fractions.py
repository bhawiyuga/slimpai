"""
Fractions Question Bank
All questions related to fractions topic
"""

FRACTIONS_BANK = {
    "baseline": [
        {
            "question": "Which fraction shows one part of a whole that is divided into two equal parts?",
            "options": ["1/2", "1/4", "1/3"],
            "correct_answer_index": 0,
            "explanation": "1/2 means one out of two equal parts, which is half."
        },
        {
            "question": "If you have a pizza cut into 4 equal slices and you eat 1 slice, what fraction of the pizza did you eat?",
            "options": ["1/2", "1/4", "1/3"],
            "correct_answer_index": 1,
            "explanation": "You ate 1 out of 4 slices, which is written as 1/4."
        },
        {
            "question": "Which fraction is larger: 1/2 or 1/4?",
            "options": ["1/2", "1/4", "They are the same"],
            "correct_answer_index": 0,
            "explanation": "1/2 is half, while 1/4 is a quarter. Half is larger than a quarter."
        }
    ],
    "lessons": {
        "Understanding Fractions Basics": {
            "content": "🍕 Hey there! Let's talk about fractions using pizza! 🍕\n\nA **fraction** is like sharing a pizza fairly. When we write 1/2, we're saying:\n- The **bottom number (2)** = how many equal pieces the pizza is cut into\n- The **top number (1)** = how many pieces you get\n\nSo 1/2 means you get 1 piece out of 2 equal pieces - that's half the pizza! 🎉\n\nThink about it:\n- 1/4 = 1 piece out of 4 pieces (a quarter)\n- 2/4 = 2 pieces out of 4 pieces (half)\n- 3/4 = 3 pieces out of 4 pieces (most of it!)",
            "quiz": {
                "question": "If a chocolate bar is divided into 8 equal pieces and you eat 3 pieces, what fraction did you eat?",
                "options": ["3/8", "8/3", "3/5"],
                "correct_answer_index": 0,
                "explanation": "You ate 3 pieces out of 8 total pieces, which is 3/8."
            }
        },
        "Comparing Fractions": {
            "content": "🎯 Now let's learn to compare fractions!\n\n**Same Bottom Number Rule:**\nWhen fractions have the same bottom number (denominator), the one with the bigger top number is larger!\n\nExample: 3/4 vs 1/4\n- Same bottom (4), but 3 > 1\n- So 3/4 is bigger! ✨\n\n**Different Bottom Numbers:**\nImagine two pizzas:\n- Pizza A cut into 2 pieces (you get 1/2)\n- Pizza B cut into 4 pieces (you get 1/4)\n\nWhich piece is bigger? The one from Pizza A! So 1/2 > 1/4.\n\nThe smaller the bottom number, the bigger each piece! 🍕",
            "quiz": {
                "question": "Which fraction is larger: 2/3 or 2/5?",
                "options": ["2/3", "2/5", "They are the same"],
                "correct_answer_index": 0,
                "explanation": "When top numbers are the same, the fraction with the smaller bottom number is larger. 2/3 > 2/5."
            }
        },
        "Adding Fractions": {
            "content": "➕ Time to add fractions!\n\n**Same Bottom Number (Easy!):**\nWhen fractions have the same bottom, just add the top numbers!\n\nExample: 1/4 + 2/4 = ?\n- Keep the bottom: 4\n- Add the tops: 1 + 2 = 3\n- Answer: 3/4 ✅\n\n**Think of it like pizza:**\n- You have 1 slice of a 4-slice pizza\n- Your friend gives you 2 more slices\n- Now you have 3 slices out of 4!\n\n**Remember:** Only add the TOP numbers, keep the bottom the same! 🎉",
            "quiz": {
                "question": "What is 2/6 + 3/6?",
                "options": ["5/6", "5/12", "6/6"],
                "correct_answer_index": 0,
                "explanation": "Add the top numbers: 2 + 3 = 5. Keep the bottom: 6. Answer: 5/6."
            }
        },
        "Subtracting Fractions": {
            "content": "➖ Let's learn to subtract fractions!\n\n**Same Bottom Number (Just like addition!):**\nWhen fractions have the same bottom, just subtract the top numbers!\n\nExample: 3/4 - 1/4 = ?\n- Keep the bottom: 4\n- Subtract the tops: 3 - 1 = 2\n- Answer: 2/4 (which is the same as 1/2!) ✅\n\n**Think of it like cookies:**\n- You have 3 cookies out of 4\n- You eat 1 cookie\n- Now you have 2 cookies out of 4 left!\n\n**Remember:** Only subtract the TOP numbers, keep the bottom the same! 🍪",
            "quiz": {
                "question": "What is 5/8 - 2/8?",
                "options": ["3/8", "7/8", "3/16"],
                "correct_answer_index": 0,
                "explanation": "Subtract the top numbers: 5 - 2 = 3. Keep the bottom: 8. Answer: 3/8."
            }
        },
        "Equivalent Fractions": {
            "content": "🔄 Let's discover equivalent fractions!\n\n**What are equivalent fractions?**\nDifferent fractions that represent the same amount!\n\nExample: 1/2 = 2/4 = 4/8\n- All these mean \"half\"!\n\n**How to find them:**\nMultiply both the top AND bottom by the same number!\n\nExample: 1/3 × 2/2 = 2/6\n- We multiplied both by 2\n- 1/3 and 2/6 are equivalent! ✨\n\n**Why is this useful?**\nIt helps us compare and add fractions with different bottoms!\n\nThink of pizza:\n- 1/2 of a pizza cut into 2 pieces\n- 2/4 of a pizza cut into 4 pieces\n- Same amount of pizza! 🍕",
            "quiz": {
                "question": "Which fraction is equivalent to 2/3?",
                "options": ["4/6", "3/4", "2/5"],
                "correct_answer_index": 0,
                "explanation": "2/3 × 2/2 = 4/6. Both fractions represent the same amount."
            }
        }
    }
}
