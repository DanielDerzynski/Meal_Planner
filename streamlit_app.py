import streamlit as st
from openai import OpenAI
import pandas as pd

# Klucz API OpenAI
client = OpenAI(api_key="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")

def generate_meal_plan(calories, exclusions, meals_per_day, budget, allergies):
    """Generowanie planu posiłków, przepisów i listy zakupów przy użyciu OpenAI."""
    prompt = f"""
    Stwórz plan posiłków na 7 dni, uwzględniając następujące wymagania:
    - Dzienna liczba kalorii: {calories} kcal
    - Produkty wykluczone: {exclusions}
    - Liczba posiłków dziennie: {meals_per_day}
    - Budżet dzienny: {budget} zł
    - Składniki alergiczne: {allergies}

    Plan posiłków powinien zawierać szczegółowe przepisy na każdy posiłek, w tym składniki i sposób przygotowania. Na końcu planu dodaj również listę zakupów obejmującą wszystkie składniki, które będą potrzebne do przygotowania tych posiłków. Rozdziel posiłki na dni i uwzględnij w opisach każdy składnik oraz instrukcje przygotowania.
    """

    response = client.chat.completions.create(model="gpt-3.5-turbo",  # Możesz użyć też gpt-4, jeśli masz dostęp
    messages=[
        {"role": "system", "content": "Jesteś asystentem kulinarnym pomagającym w planowaniu posiłków."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=1500)

    return response.choices[0].message.content

def save_to_excel(plan_text):
    """Zapisuje plan posiłków, przepisy i listę zakupów do pliku Excel."""
    days = plan_text.split("Dzień")
    data = []
    shopping_list = set()
    recipe_details = []

    for day in days[1:]:
        lines = day.strip().split("\n")
        day_name = lines[0].strip()
        for line in lines[1:]:
            if line.strip():
                if "-" in line:
                    meal, description = line.split("-", 1)
                    # Dodajemy posiłek do planu
                    data.append([day_name, meal.strip(), description.strip()])
                    # Dodajemy składniki posiłku do listy zakupów
                    ingredients = extract_ingredients(description)
                    shopping_list.update(ingredients)
                    # Dodajemy szczegóły przepisu
                    recipe_details.append([meal.strip(), description.strip()])

    # Tworzymy DataFrame z planem posiłków
    df = pd.DataFrame(data, columns=["Dzień", "Posiłek", "Opis"])

    # Tworzymy listę zakupów
    shopping_list = list(shopping_list)
    shopping_list.sort()

    # Określamy ścieżkę i zapisujemy plik w folderze tymczasowym
    file_path = "/tmp/PlanPosilkow.xlsx"
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Plan Posiłków", index=False)

        # Dodajemy arkusz z listą zakupów
        shopping_df = pd.DataFrame(shopping_list, columns=["Lista Zakupów"])
        shopping_df.to_excel(writer, sheet_name="Lista Zakupów", index=False)
        
        # Dodajemy arkusz z przepisami
        recipes_df = pd.DataFrame(recipe_details, columns=["Posiłek", "Przepis"])
        recipes_df.to_excel(writer, sheet_name="Przepisy", index=False)

    return file_path

def extract_ingredients(description):
    """Funkcja do ekstrakcji składników z opisu przepisu."""
    # Zakładamy, że składniki będą zaczynać się od słowa 'Składniki:'
    ingredients = []
    if "Składniki:" in description:
        ingredients_start = description.split("Składniki:")[1]
        ingredients = [ingredient.strip() for ingredient in ingredients_start.split(",")]
    return ingredients

def main():
    st.title("Planowanie posiłków")

    # Zbieranie danych od użytkownika
    st.header("Dostosuj swój plan posiłków")
    calories = st.number_input("Ile spożywasz/chcesz spożywać kcal dziennie?", min_value=1000, max_value=5000, step=100)
    exclusions = st.text_area("Jakie produkty nie są/nie mogą być w twojej diecie?")
    meals_per_day = st.slider("Ile posiłków dziennie chcesz spożywać?", min_value=1, max_value=6, step=1)
    budget = st.number_input("Ile chcesz przeznaczać pieniędzy na posiłki na dzień?", min_value=10.0, max_value=200.0, step=5.0)
    allergies = st.text_area("Czy jesteś uczulony/na na jakieś składniki?")

    if st.button("Generuj plan posiłków"):
        st.info("Generowanie planu posiłków. Proszę czekać...")
        meal_plan = generate_meal_plan(calories, exclusions, meals_per_day, budget, allergies)
        st.success("Plan posiłków został wygenerowany!")
        st.text_area("Plan posiłków", meal_plan, height=300)

        # Zapisujemy plan do pliku Excel
        file_path = save_to_excel(meal_plan)
        
        # Przycisk do pobrania pliku Excel
        st.download_button(
            label="Pobierz plan posiłków", 
            data=open(file_path, "rb").read(), 
            file_name="PlanPosilkow.xlsx", 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Możliwość modyfikacji
    st.header("Czy taki plan Ci odpowiada?")
    feedback = st.radio("Opcje:", ("Tak, jest idealny!", "Nie, chciałbym wprowadzić zmiany."))

    if feedback == "Nie, chciałbym wprowadzić zmiany.":
        st.text_area("Opisz, co chciałbyś zmienić w planie:", height=100)
        st.button("Prześlij poprawki")

if __name__ == "__main__":
    main()
