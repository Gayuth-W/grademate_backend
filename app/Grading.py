import ast 
import json 
import time
import re
import pandas as pd 
import google.generativeai as genai

genai.configure(api_key="AIzaSyDjPct6uE3e4Ytsbvyi_N6Ptos8i6LJgaU")

def grade_question(qnum, student_ans, rubric_text, max_mark=1): 
    prompt = f"""
    You are an examiner. Grade this student's answer.

    Question {qnum}: 

    Student Answer: 
    {student_ans} 

    Mark Scheme: 
    {rubric_text} 

    Rules: 
    - Award a score between 0 and {max_mark}.
    - Give one short feedback sentence. 
    - Give one recommendation for improvement. 
    - Return JSON only. 
    {{
      "score": number, 
      "feedback": "string", 
      "recommendation": "string"
    }}
    """

    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        raw = match.group(0)

    raw = re.sub(r",\s*}", "}", raw)
    raw = re.sub(r",\s*]", "]", raw)

    try:
        return json.loads(raw)
    except Exception:
        return {"error": f"Parse error: {raw}"}


def parse_misc(misc_txt): 
    answers = {}
    
    # Clean up the text
    text = misc_txt.replace("\n", " ").strip()
    
    # Split by question numbers first
    question_parts = re.split(r'\b(\d+)\s*\)', text)
    
    for i in range(1, len(question_parts), 2):
        if i + 1 < len(question_parts):
            q_num = question_parts[i].strip()
            q_content = question_parts[i + 1].strip()
            
            if q_num and q_content:
                answers[q_num] = parse_question_content(q_content)
    
    return answers

def parse_question_content(content):
    """Parse the content of a single question"""
    roman_parts = {}
    
    # Split by roman numerals (I, II, III, IV, V, etc.)
    roman_sections = re.split(r'\b(I{1,3}|IV|V|VI{0,3}|IX|X)\s*[\.\)]', content, flags=re.IGNORECASE)
    
    for i in range(1, len(roman_sections), 2):
        if i + 1 < len(roman_sections):
            roman_num = roman_sections[i].lower()
            roman_content = roman_sections[i + 1].strip()
            
            if roman_num and roman_content:
                # Check if this roman part has sub-parts (with optional spaces)
                if re.search(r'\(\s*[a-z]\s*\)', roman_content):
                    # Has sub-parts - use a more sophisticated approach
                    sub_parts = {}
                    
                    # Find all sub-parts and their positions (with optional spaces)
                    sub_matches = list(re.finditer(r'\(\s*([a-z])\s*\)', roman_content))
                    
                    for idx, match in enumerate(sub_matches):
                        sub_letter = match.group(1).lower()
                        start_pos = match.end()
                        
                        # Find the end position (start of next sub-part or end of string)
                        if idx + 1 < len(sub_matches):
                            end_pos = sub_matches[idx + 1].start()
                        else:
                            end_pos = len(roman_content)
                        
                        sub_content = roman_content[start_pos:end_pos].strip()
                        # Clean up the sub-content
                        sub_content = re.sub(r'^\s*[\.\)]\s*', '', sub_content)
                        sub_parts[sub_letter] = sub_content
                    
                    roman_parts[roman_num] = sub_parts
                else:
                    # No sub-parts, just text
                    roman_content = re.sub(r'^\s*[\.\)]\s*', '', roman_content)
                    roman_parts[roman_num] = roman_content.strip()
    
    return roman_parts



def grade_student(std_id, std_answers, ms): 
    total_score = 0
    total_max = 0
    feedback_log = []
    recom_log = [] 

    for q, q_data in ms.items(): 
        # Try to match question numbers (handle "01" vs "1" mismatch)
        std_q = std_answers.get(q, {})
        if not std_q:
            # Try with zero-padded version
            std_q = std_answers.get(f"{int(q):02d}", {})
        if not std_q:
            # Try without zero padding
            std_q = std_answers.get(str(int(q)), {}) 

        for roman, roman_data in q_data["roman_parts"].items(): 
            std_roman = std_q.get(roman, "") 

            if roman_data.get("sub_parts"): 
                for sub, sub_data in roman_data["sub_parts"].items():
                    std_sub = std_roman.get(sub, "") if isinstance(std_roman, dict) else ""
                    rubric_text = sub_data.get("text", "") 
                    max_mark = sub_data.get("marks", 1) 
                    total_max += max_mark

                    result = grade_question(f"{q}{roman}{sub}", std_sub, rubric_text, max_mark)

                    if "error" in result: 
                        feedback_log.append(f"Q{q}{roman}{sub}: {result['error']}")
                        recom_log.append(f"Q{q}{roman}{sub}: No recommendations (parse error)")
                        continue
                    
                    score = result.get("score", 0)
                    total_score += score
                    feedback_log.append(f"Q{q}{roman}{sub}: {result.get('feedback', '')}")
                    recom_log.append(f"Q{q}{roman}{sub}: {result.get('recommendation', '')}")

            else:
                rubric_text = roman_data.get("text", "")
                max_mark = roman_data.get("marks", 1)
                total_max += max_mark

                result = grade_question(f"{q}{roman}", std_roman, rubric_text, max_mark)

                if "error" in result: 
                    feedback_log.append(f"Q{q}{roman}: {result['error']}")
                    recom_log.append(f"Q{q}{roman}: No recommendations (parse error)")
                    continue
                
                score = result.get("score", 0)
                total_score += score
                feedback_log.append(f"Q{q}{roman}{sub if 'sub' in locals() else ''}: {result.get('feedback', '')}")
                recom_log.append(f"Q{q}{roman}{sub if 'sub' in locals() else ''}: {result.get('recommendation', '')}")

            time.sleep(2)


    data_frame = pd.DataFrame([{"student_id": std_id, 
                                "score": f"{total_score}/{total_max}"
    }])
    data_frame.to_excel("results.xlsx", index=False) 

    feedback_log.append(f"Total Score: {total_score}/{total_max}")
    with open("feedback.txt", "w", encoding="utf-8") as file: 
        text = file.write("\n".join(feedback_log))

    with open("recommendations.txt", "w", encoding="utf-8") as file:
        text = file.write("\n".join(recom_log))

    print("Done updating results.xlsx, feedback.txt and recommendations.txt")


def main(): 
    with open("marking_scheme_extracted.json") as file: 
        ms = json.load(file)

    with open("output_questions2.json") as file: 
        std_data = json.load(file) 

    std_id = std_data["student_id"] 
    std_answers  = parse_misc(std_data["answers"])
    

    grade_student(std_id, std_answers, ms)

if __name__ == "__main__": 
    main() 
