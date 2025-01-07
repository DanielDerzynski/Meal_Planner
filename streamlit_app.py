import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components

# CSS dla zmiany tła
st.markdown(
    """
    <style>
    .stApp {
        background-color: #b3d9ff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def generate_meal_plan_day(prompt, client):
    """Generowanie planu posiłków na jeden dzień przy użyciu OpenAI."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Możesz użyć też gpt-4, jeśli masz dostęp
        messages=[
            {"role": "system", "content": "Jesteś asystentem kulinarnym pomagającym w planowaniu posiłków."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500  # Mniejsza liczba tokenów dla odpowiedzi na jeden dzień
    )
    return response.choices[0].message.content

def generate_meal_plan(calories, exclusions, meals_per_day, budget, allergies, client):
    """Generowanie planu posiłków na trzy dni."""
    prompts = [
        f"Stwórz plan posiłków na dzień 1, uwzględniając następujące wymagania:\n"
        f"- Dzienna liczba kalorii: {calories} kcal\n"
        f"- Produkty wykluczone: {exclusions}\n"
        f"- Liczba posiłków dziennie: {meals_per_day}\n"
        f"- Budżet dzienny: {budget} zł\n"
        f"- Składniki alergiczne: {allergies}\n\n"
        f"Plan posiłków powinien zawierać szczegółowe przepisy na każdy posiłek, w tym składniki i sposób przygotowania.Na końcu planu dodaj również listę zakupów obejmującą wszystkie składniki, które będą potrzebne do przygotowania tych posiłków. Rozdziel posiłki na dni i uwzględnij w opisach każdy składnik oraz instrukcje przygotowania.",

        f"Stwórz plan posiłków na dzień 2, uwzględniając następujące wymagania:\n"
        f"- Dzienna liczba kalorii: {calories} kcal\n"
        f"- Produkty wykluczone: {exclusions}\n"
        f"- Liczba posiłków dziennie: {meals_per_day}\n"
        f"- Budżet dzienny: {budget} zł\n"
        f"- Składniki alergiczne: {allergies}\n\n"
        f"Plan posiłków powinien zawierać szczegółowe przepisy na każdy posiłek, w tym składniki i sposób przygotowania.Na końcu planu dodaj również listę zakupów obejmującą wszystkie składniki, które będą potrzebne do przygotowania tych posiłków. Rozdziel posiłki na dni i uwzględnij w opisach każdy składnik oraz instrukcje przygotowania.",

        f"Stwórz plan posiłków na dzień 3, uwzględniając następujące wymagania:\n"
        f"- Dzienna liczba kalorii: {calories} kcal\n"
        f"- Produkty wykluczone: {exclusions}\n"
        f"- Liczba posiłków dziennie: {meals_per_day}\n"
        f"- Budżet dzienny: {budget} zł\n"
        f"- Składniki alergiczne: {allergies}\n\n"
        f"Plan posiłków powinien zawierać szczegółowe przepisy na każdy posiłek, w tym składniki i sposób przygotowania.Na końcu planu dodaj również listę zakupów obejmującą wszystkie składniki, które będą potrzebne do przygotowania tych posiłków. Rozdziel posiłki na dni i uwzględnij w opisach każdy składnik oraz instrukcje przygotowania."
    ]

    day1 = generate_meal_plan_day(prompts[0], client)
    day2 = generate_meal_plan_day(prompts[1], client)
    day3 = generate_meal_plan_day(prompts[2], client)

    return day1, day2, day3

def apply_modifications(original_plan, modifications, client):
    """Zastosowanie poprawek do istniejącego planu."""
    prompt = f"Oto oryginalny plan posiłków:\n{original_plan}\n\n"
    prompt += f"Użytkownik zasugerował następujące zmiany:\n{modifications}\n\n"
    prompt += "Zaktualizuj plan posiłków zgodnie z sugestiami użytkownika."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Jesteś asystentem kulinarnym pomagającym w planowaniu posiłków.Na końcu planu dodaj również listę zakupów obejmującą wszystkie składniki, które będą potrzebne do przygotowania tych posiłków. Rozdziel posiłki na dni i uwzględnij w opisach każdy składnik oraz instrukcje przygotowania."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500
    )

    return response.choices[0].message.content

def main():
    st.title("Planowanie posiłków")

    # Użytkownik wprowadza klucz API
    api_key = st.text_input("Wprowadź swój klucz API OpenAI:", type="password")

    if not api_key:
        st.warning("Proszę wprowadzić klucz API, aby kontynuować.")
        return

    # Inicjalizacja klienta OpenAI
    client = OpenAI(api_key=api_key)

    # Zbieranie danych od użytkownika
    st.header("Dostosuj swój plan posiłków")
    calories = st.number_input("Ile spożywasz/chcesz spożywać kcal dziennie?", min_value=1000, max_value=5000, step=100)
    exclusions = st.text_area("Jakie produkty nie są/nie mogą być w twojej diecie?")
    meals_per_day = st.slider("Ile posiłków dziennie chcesz spożywać?", min_value=1, max_value=6, step=1)
    budget = st.number_input("Ile chcesz przeznaczać pieniędzy na posiłki na dzień?", min_value=10.0, max_value=200.0, step=5.0)
    allergies = st.text_area("Czy jesteś uczulony/na na jakieś składniki?")

    if st.button("Generuj plan posiłków"):
        st.info("Generowanie planu posiłków. Proszę czekać...")
        day1, day2, day3 = generate_meal_plan(calories, exclusions, meals_per_day, budget, allergies, client)
        st.session_state["day1"] = day1
        st.session_state["day2"] = day2
        st.session_state["day3"] = day3
        st.session_state["modifications"] = ""
        st.success("Plan posiłków został wygenerowany!")

    if "day1" in st.session_state:
        st.subheader("Dzień 1:")
        st.text_area("Plan posiłków - Dzień 1", st.session_state["day1"], height=1500, key="day1_text")

        st.subheader("Dzień 2:")
        st.text_area("Plan posiłków - Dzień 2", st.session_state["day2"], height=1500, key="day2_text")

        st.subheader("Dzień 3:")
        st.text_area("Plan posiłków - Dzień 3", st.session_state["day3"], height=1500, key="day3_text")

    # Możliwość modyfikacji
    if "day1" in st.session_state:
        st.header("Czy taki plan Ci odpowiada?")
        feedback = st.radio("Opcje:", ("Tak, jest idealny!", "Nie, chciałbym wprowadzić zmiany."))

        if feedback == "Nie, chciałbym wprowadzić zmiany.":
            modifications = st.text_area("Opisz, co chciałbyś zmienić w planie:", height=100, key="modifications_text")

            if st.button("Prześlij poprawki"):
                st.session_state["modifications"] = modifications

                updated_day1 = apply_modifications(st.session_state["day1"], modifications, client)
                updated_day2 = apply_modifications(st.session_state["day2"], modifications, client)
                updated_day3 = apply_modifications(st.session_state["day3"], modifications, client)

                st.session_state["day1"] = updated_day1
                st.session_state["day2"] = updated_day2
                st.session_state["day3"] = updated_day3

                st.success("Plan został zaktualizowany na podstawie Twoich sugestii!")

                st.subheader("Zaktualizowany plan - Dzień 1:")
                st.text_area("Plan posiłków - Dzień 1", updated_day1, height=300)

                st.subheader("Zaktualizowany plan - Dzień 2:")
                st.text_area("Plan posiłków - Dzień 2", updated_day2, height=300)

                st.subheader("Zaktualizowany plan - Dzień 3:")
                st.text_area("Plan posiłków - Dzień 3", updated_day3, height=300)

if __name__ == "__main__":
    main()
