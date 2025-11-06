import pandas as pd
from faker import Faker
import random
import re
from datetime import datetime, timedelta, time
import time as time_module  # Alias to avoid conflict with datetime.time
from faker.providers import BaseProvider
from geopy.geocoders import Nominatim
import unicodedata
geolocator = Nominatim(user_agent="cz_city_locator")
class CzechRegionCityProvider(BaseProvider):
    # Example lists for regions — customize as needed

    SOUTH_MORAVIA = [
        "Blansko", "Blatnice pod Svatým Antonínkem", "Blučina", "Boskovice", "Brno", "Břeclav", 
        "Bučovice", "Dolní Kounice", "Dubňany", "Hodonín", "Hustopeče", "Ivančice", "Jedovnice", 
        "Klobouky u Brna", "Kuřim", "Kyjov", "Letovice", "Mikulov", "Miroslav", "Modřice", 
        "Moravský Krumlov", "Moravská Nová Ves", "Oslavany", "Pohořelice", "Rájec-Jestřebí", 
        "Rousínov", "Slavkov u Brna", "Strážnice", "Šlapanice", "Tišnov", "Velká nad Veličkou", 
        "Veselí nad Moravou", "Vracov", "Vyškov", "Znojmo", "Židlochovice", "Bzenec", "Brumovice", 
        "Dolní Dunajovice", "Kobylí", "Lednice", "Mikulčice", "Mutěnice", "Pavlov", "Perná", 
        "Ratíškovice", "Terezín u Hodonína", "Valtice", "Velké Pavlovice"
    ]
    
    def regional_city(self, region=None):
        """Return a random city from the specified region. If region is None, returns from SOUTH_MORAVIA."""
        if region == "SOUTH_MORAVIA" or region is None:
            return random.choice(self.SOUTH_MORAVIA)
        # Add more regions here as needed
        return random.choice(self.SOUTH_MORAVIA)

def round_time_to_30min(t: time) -> time:
    """Round time to nearest 30 minutes"""
    minutes = t.minute
    if minutes < 15:
        rounded_minutes = 0
        hour = t.hour
    elif minutes < 45:
        rounded_minutes = 30
        hour = t.hour
    else:  # 45-59, round up to next hour
        rounded_minutes = 0
        hour = (t.hour + 1) % 24
    return time(hour, rounded_minutes, 0)

def working_hour_timestamp(fake: Faker,start_hour=9, end_hour=17):
    # generate a random date (today or this year)
    random_date = fake.date_between(start_date='-1y', end_date='today')
    
    # pick a random time within working hours
    random_hour = random.randint(start_hour, end_hour)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    
    return datetime.combine(random_date, datetime.min.time()) + timedelta(
        hours=random_hour, minutes=random_minute, seconds=random_second
    )

def manager_time_availability(fake: Faker) -> tuple[time, time]:
    dostupnost_od = round_time_to_30min(working_hour_timestamp(fake, start_hour=9, end_hour=10).time())
    dostupnost_do = round_time_to_30min(working_hour_timestamp(fake, start_hour=14, end_hour=17).time())
    return dostupnost_od, dostupnost_do

def get_email(string: str) -> str:
    """
    Generate an email address from a name string.
    Removes common academic and professional titles before generating the email.
    
    Args:
        string: Name string that may contain titles (e.g., "Dr. Jan Novák", "Prof. Ing. Marie Svobodová")
    
    Returns:
        Email address in format: firstnamelastname@example.com
    """
    # Common titles to remove (Czech and international) - with word boundaries
    titles = [
        r'\bDr\.?\s*', r'\bProf\.?\s*', r'\bIng\.?\s*', r'\bMUDr\.?\s*', r'\bPhDr\.?\s*',
        r'\bRNDr\.?\s*', r'\bMgr\.?\s*', r'\bBc\.?\s*', r'\bPh\.?D\.?\s*', r'\bPhD\.?\s*',
        r'\bDoc\.?\s*', r'\bThDr\.?\s*', r'\bJUDr\.?\s*', r'\bMVDr\.?\s*', r'\bPaedDr\.?\s*',
        r'\bPharmDr\.?\s*', r'\bThLic\.?\s*', r'\bThMgr\.?\s*', r'\bCSs\.?\s*'
    ]
    
    # Remove titles (anywhere in the string)
    cleaned = string
    for title_pattern in titles:
        cleaned = re.sub(title_pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Remove commas and extra whitespace, then convert to email format
    cleaned = unicodedata.normalize('NFD', cleaned)
    cleaned = re.sub(r'[^\w]+', '', cleaned.strip())
    return cleaned.lower() + "@retail.com"


def generate_mock_data() -> pd.DataFrame:
    fake = Faker('cs_CZ')
    fake.add_provider(CzechRegionCityProvider)  # Add the custom provider
    
    # Verify the provider is registered
    if not hasattr(fake, 'regional_city'):
        raise RuntimeError("CzechRegionCityProvider not properly registered")

    # Configuration
    num_stores = 20        # number of stores

    # Generate mock data
    data = []


    for obchod_id in range(1, num_stores + 1):
        mesto = fake.regional_city()  
        jmeno_manazera = fake.name()
        email_manazera = get_email(jmeno_manazera) #tohle jeste doladit, aby to bylo validni email
        trzby_v_kc = round(random.uniform(200000, 700000), 2)
        location = geolocator.geocode(f"{mesto}, Czech Republic") # Now it's a method on the fake object
        lat = location.latitude
        lng = location.longitude
        pocet_transakci = random.randint(150, 300)
        prumerna_trzba_na_transakci = round(trzby_v_kc / pocet_transakci, 2)
        trzby_za_predesly_tyden = round(random.uniform(200000, 700000), 2)
        zmena_oproti_predeslemu_tydnu = round((trzby_v_kc - trzby_za_predesly_tyden) / trzby_za_predesly_tyden * 100, 2)
        dostupnost_zbozi = round(random.uniform(85, 100), 2) if zmena_oproti_predeslemu_tydnu > 0 else (100 + (45*zmena_oproti_predeslemu_tydnu/100))
        dostupnost_personal = round(random.uniform(90, 100), 2) if zmena_oproti_predeslemu_tydnu > 0 else (100 + (35*zmena_oproti_predeslemu_tydnu/100))
        plneni_cilu = round(random.uniform(0.8, 1.2), 2)
        posledni_navsteva = working_hour_timestamp(fake).date()
        dostupnost_utery_od, dostupnost_utery_do = manager_time_availability(fake)
        dostupnost_streda_od, dostupnost_streda_do = manager_time_availability(fake)
        dostupnost_ctvrtek_od, dostupnost_ctvrtek_do = manager_time_availability(fake)
        time_module.sleep(1)  # Use time module alias to avoid conflict with datetime.time

        data.append([
            obchod_id,
            mesto,
            jmeno_manazera,
            email_manazera,
            trzby_v_kc,
            lat,
            lng,
            pocet_transakci,
            prumerna_trzba_na_transakci,
            trzby_za_predesly_tyden,
            zmena_oproti_predeslemu_tydnu,
            dostupnost_zbozi,
            dostupnost_personal,    
            plneni_cilu,
            posledni_navsteva,
            dostupnost_utery_od,
            dostupnost_utery_do,
            dostupnost_streda_od,
            dostupnost_streda_do,
            dostupnost_ctvrtek_od,
            dostupnost_ctvrtek_do
        ])

    # Create DataFrame
    columns = [
        "Obchod_ID","Město","Jméno_Manažera","Email_Manažera",
        "Tržby_v_Kc","Lat","Lng","Počet_Transakcí","Průměrná_Tržba_na_Transakci",
        "Tržby_za_Předešlý_Týden",
        "Změna_Oproti_Předešlému_Týdnu (%)", "Dostupnost_Zboží (%)", "Dostupnost_Personal (%)", "Plnění_Cílů",
        "Poslední_Návštěva",
        "Dostupnost_Utery_Od",
        "Dostupnost_Utery_Do",
        "Dostupnost_Streda_Od",
        "Dostupnost_Streda_Do", 
        "Dostupnost_Ctvrtek_Od",
        "Dostupnost_Ctvrtek_Do"
    ]

    df = pd.DataFrame(data, columns=columns)

    # Save to CSV
    df.to_csv("./data/mock_retail_data.csv", index=False)
    print("✅ mock_retail_data.csv created successfully!")
    print(df.head())

    return df

if __name__ == "__main__":
    mocked_retail_data = generate_mock_data()
    #mocked_calendar_data = generate_mock_calendar_data(mocked_retail_data)