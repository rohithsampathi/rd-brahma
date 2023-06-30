from flask import Flask, render_template, request, jsonify
import openai
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

class Config:
    OPENAI_API_KEY = "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"

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object(Config)

Base = declarative_base()

# Initialize OpenAI
openai.api_key = app.config["OPENAI_API_KEY"]

class GptTokenUsage(Base):
    __tablename__ = 'token_usage'
    id = Column(Integer, primary_key=True)
    generation_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Path to the SQLite file
db_file = 'sqlite:///token_usage.db'

# Creating engine and binding it to the Base class
engine = create_engine(db_file)
Base.metadata.create_all(engine)

# Create a session to access the database
Session = sessionmaker(bind=engine)

def rephrase_text(body, keywords):
    writing_style = f"""
        You are a master SEO GPT. You are also a market researcher who mastered effective communication of market intelligence to readers. Your purpose is to rephrase the below input text and SEO optimising it with the provided keywords.

        Must Follows:
        1. Use the below keywords in exact phrases within the content for SEO optimisation at least three times.
        2. Output should be 100% human-like and not like AI generated
        3. Keep the tone realistic and use simple human words.
        4. Keep the language persuasive and professional
        5. Do not reduce the length of the input content. Expand wherever possible and make the description informative
        6. Keep the output in not less than 1400 words

        Note: Make the output SEO optimised for the provided keywords below. Use the keywords in exact within the text. Make the content persuasive for the reader to download sample report. Do not change the existing side headings.

            ------------------------- End of Instructions -------------------------


        """

    # GPT-4 chat model processing with news_content as input
    try:
        print("Before GPT-4 API call")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"{writing_style}"},
                {"role": "user", "content": f"Input Text: {body} \n Keywords: {keywords} ------------ End of Input. Give the output below -------- \n "},
            ],
            temperature=0.7,
            max_tokens=3000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.3,
        )
        print("After GPT-4 API call")
        result = response.choices[0].message['content'].strip()
        num_tokens = response['usage']['total_tokens'] if 'usage' in response and 'total_tokens' in response['usage'] else 0

        # Prepare the output
        output = {"result": result}

        # Calculating the cost
        cost = 0.06 * num_tokens / 1000

        # Insert the token usage details into SQLite database
        session = Session()
        token_entry = GptTokenUsage(generation_tokens=num_tokens,
                                     total_tokens=num_tokens,
                                     cost=cost)
        session.add(token_entry)
        session.commit()

        # Fetch the total tokens and total cost used so far
        total_tokens_so_far = session.query(
            func.sum(GptTokenUsage.total_tokens)).scalar()
        total_cost_so_far = session.query(
            func.sum(GptTokenUsage.cost)).scalar()

        print(f"Tokens used in this generation: {num_tokens}")
        print(f"Cost for this generation: ${cost:.5f}")
        print(f"Total tokens used so far: {total_tokens_so_far}")
        print(f"Total cost so far: ${total_cost_so_far:.5f}")
        
        session.close()
        
        return output

    except Exception as e:
        print(f"Error in generate function: {str(e)}")
        return {"result": "An error occurred during generation"}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/rephrase", methods=["POST"])
def generate():
    try:
        body = request.form["body"]
        keywords = request.form["keywords"]

        result = rephrase_text(body, keywords)
        output = {"result": result["result"]}
        
        return jsonify(output)

    except Exception as e:
        print("Error in generate endpoint: ", e)
        return jsonify(error=str(e)), 500

@app.errorhandler(500)
def server_error(e):
    print("Internal server error: ", str(e))
    return jsonify(error='Internal server error'), 500

if __name__ == "__main__":
    app.run(debug=True)