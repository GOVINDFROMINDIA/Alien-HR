import numpy as np
from typing import Any
import openai
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
openai.api_key = "paste ur api key"

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

class ResumeAnalyser():

    def __init__(self) -> None:
        pass

    def __call__(self, resume_cv : str, job_description : str, discount_factor = 0.15) -> Any:
        negative_score = 0
        response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                        "role": "system",
                        "content": "You are an AI assistant who when provided with a resume and CV along with a job description by the user, you provide the requirements that are met on the resume and CV for the job description, and also requirements that are not met on the resume and CV for the job description. Use the prefix 'Requirements met on the resume and CV:' and 'Requirements not met on the resume and CV:'.Only Answer based on Resume and CV, don't make stuff up.If none not mentioned say 'None'."
                        },
                        {
                        "role": "user",
                        "content": f"{resume_cv}"
                        }
                    ],
                    temperature=0.5,
                    max_tokens=356,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
        )

        resp = response['choices'][0]['message']['content']
        idx1 = resp.find("Requirements met on the resume and CV:")
        idx2 = resp.find("Requirements not met on the resume and CV:")

        present = resp[idx1+len("Requirements met on the resume and CV:"):idx2]
        not_present = resp[idx2+len("Requirements not met on the resume and CV:"):]


        # print(f"{present}\n\n")
        # print(f"{not_present}\n\n")
        job_description_embs = get_embedding(job_description)

        present_embs = get_embedding(present)

        positive_score = cosine_similarity([present_embs],[job_description_embs])

        # print(positive_score)
        R = fuzz.token_sort_ratio(not_present.lower, 'none')
        if R < 0.9:
            not_present_embs = get_embedding(not_present)
            negative_score = cosine_similarity([not_present_embs],[job_description_embs])
        # print(positive_score, negative_score*discount_factor)
        # print(f"Total Score:{positive_score-(negative_score*discount_factor)}")
        total_score = positive_score-(negative_score*discount_factor)
        return total_score


class Interview_Chat():

    def __init__(self) -> None:
        # self.prev_gen_length = 0
        pass

    def __call__(self, skills : list):
        output = []

        for skill in skills:
            questions = []
            answers = []

            messages = [
                {
                "role": "system",
                "content": "You are an Interview bot assigned with asking one word technical answer questions and answers to those questions based on the skills provided by the user. The questions should be able to test there skills. Use prefixes 'Q:' and 'A:'. Ask tough questions. There should be 10 questions."
                },
                {
                "role": "user",
                "content": f"Skills:{skill}"
                },
            ]

            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            temperature=0.5,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )

            resp = response['choices'][0]['message']['content']

            splits = resp.split("Q:")
            
            for split in splits[1:]:
                try:
                    k = split.split("A:")
                    # print(split)
                    # print(f"{k[0]} : {k[1]}")
                    questions.append(k[0])
                    answers.append(k[1])
                except Exception:
                    pass
            output.append((questions, answers))

            # self.prev_gen_length = len(questions)

        return output
            


if __name__ == "__main__":

    Chat = Interview_Chat()


#     output = Chat(["""Skills:
# Python, C, Java
# pandas
# ML and DL using pytorch
# Sklearn
# Flask
# Arduino
# Raspberry Pi"""])
#     print(len(output))
#     print(len(output[0]))
#     print(len(output[0][0]))

    output = Chat(["""Skills:
Python, C, Java
pandas
ML and DL using pytorch
Sklearn
Flask
Arduino
Raspberry Pi""","""Skills: Blender
msoffice
Arduino
Raspberry Pi"""])
    print(len(output))
    print(len(output[0]))
    print(len(output[0][0]))
