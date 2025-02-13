import streamlit as st
import pandas as pd
try:
    import plotly.graph_objects as go
    import plotly.express as px
except ModuleNotFoundError as e:
    st.error(f"Erreur de module : {e}")

# Configuration de la page
st.set_page_config(page_title="TUMA PLUS", layout="wide")

# Affichage du logo et du titre
st.image("logo.jpg", width=600)
st.title("TABLEAU DE BORD DU CONSORTIUM TUMA PLUS")


# Connexion aux données avec actualisation automatique
DATA_URL = "https://kc.humanitarianresponse.info/api/v1/data/1560805.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(DATA_URL)
    return df
data = load_data()

# Bouton d'actualisation des données
if st.button("Actualiser les données 🔄"):
    st.cache_data.clear()  # Efface le cache pour forcer le rechargement des données
    st.rerun()  # Recharge l'application avec les nouvelles données

st.write(f"Nombre d'enregistrements sur le serveur : **{len(data)}**")    
# Filtrage des colonnes
st.sidebar.header("Filtrage des données")

# 1. Filtre sur les organisations
organisation = st.sidebar.multiselect(
    "Nom de l'organisation",
    options=data["organisation"].unique(), 
    key="organisation_filter"
)

# 2. Filtre sur les provinces
province = st.sidebar.multiselect(
    "Province", 
    options=data["Province"].unique(), 
    key="province_filter"
)

# 3. Filtre sur les zones de santé (Zone_sante) dépendant des provinces
if province:
    filtered_for_zone = data[data["Province"].isin(province)]
    zone_sante = st.sidebar.multiselect(
        "Zone de santé", 
        options=filtered_for_zone["Zone_sante"].unique(), 
        key="zone_sante_filter"
    )
else:
    zone_sante = st.sidebar.multiselect(
        "Zone de santé", 
        options=data["Zone_sante"].unique(), 
        key="zone_sante_filter"
    )

# 4. Filtre sur les aires de santé (Aire_sante) dépendant des zones de santé
if zone_sante:
    filtered_for_aire = filtered_for_zone[filtered_for_zone["Zone_sante"].isin(zone_sante)]
    aire_sante = st.sidebar.multiselect(
        "Aire de santé", 
        options=filtered_for_aire["Aire_sante"].unique(), 
        key="aire_sante_filter"
    )
else:
    aire_sante = st.sidebar.multiselect(
        "Aire de santé", 
        options=data["Aire_sante"].unique(), 
        key="aire_sante_filter"
    )

# 5. Filtre sur la période de rapportage
data["time"] = pd.to_datetime(data["time"], errors="coerce")
data["Période"] = data["time"].dt.to_period("M")
periode = st.sidebar.multiselect("Période de rapportage", options=data["Période"].dropna().unique())

import streamlit as st

# Fonction pour afficher les contacts du développeur dans la barre latérale
def developer_contacts():
    st.sidebar.header("AAP & Database Specialist - Python Developper - CARE DRC")
    st.sidebar.markdown("""
    - **Nom** : Michel Kamwanga Clark
    - **Email** : [michel.kamwanga@care.org](mailto:michel.kamwanga@care.org)
    - **Téléphone** : +243 975582294
    - **LinkedIn** : [Profil LinkedIn](https://www.linkedin.com/in/michel-kamwanga-5377b4126)
    """)

# Appel de la fonction pour afficher les contacts
developer_contacts()

# Ajouter un logo en bas des contacts
# Assurez-vous d'avoir l'image dans le même répertoire ou de spécifier le chemin complet
st.sidebar.markdown("---")  # Ligne de séparation
st.sidebar.image("care.png", width=150)  # Remplacez "logo.png" par votre fichier image

# Application des filtres
filtered_data = data.copy()

if organisation:
    filtered_data = filtered_data[filtered_data["organisation"].isin(organisation)]
if province:
    filtered_data = filtered_data[filtered_data["Province"].isin(province)]
if zone_sante:
    filtered_data = filtered_data[filtered_data["Zone_sante"].isin(zone_sante)]
if aire_sante:
    filtered_data = filtered_data[filtered_data["Aire_sante"].isin(aire_sante)]
if periode:
    filtered_data = filtered_data[filtered_data["Période"].isin(periode)]


# Fonction pour afficher les métriques avec un style personnalisé
def styled_metric(label, value):
    """Affiche une métrique avec un style personnalisé."""
    st.markdown(f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border: 2px solid green;
            border-radius: 5px;
            background-color: orange;
            color: black;
            font-size: 22px;
            font-weight: bold;
            padding: 5px;
            margin: 3px;
            text-align: center;
        ">
            <div style="font-size: 12px; font-weight: normal;">{label}</div>
            <div>{value}</div>
        </div>
    """, unsafe_allow_html=True)

# 1. PARTICIPATION CURSUS
if "PARDE" in organisation or "SARCAF" in organisation:
    filtered_participation = filtered_data

    st.header("1. PARTICIPATION CURSUS")

    col1, col2, col3, col4, col5a, col5b, col5c, col5d = st.columns(8)

    # a) Nombre de groupes
    nombre_groupes = filtered_participation["Nom_group"].count()
    with col1:
        styled_metric("Nombre de groupes", int(nombre_groupes))

    # b) Effectif début cursus
    effectif_debut = filtered_participation["Information_groupe/Effectif_debut"].sum()
    with col2:
        styled_metric("Effectif début cursus", int(effectif_debut))

    # c) Effectif fin cursus
    effectif_fin = filtered_participation["Information_groupe/Effectif_fin"].sum()
    with col3:
        styled_metric("Effectif fin cursus", int(effectif_fin))

    # d) Taux d'achèvement de cursus en pourcentage
    taux_achevement = (effectif_fin / effectif_debut) * 100 if effectif_debut > 0 else 0
    with col4:
        styled_metric("Taux d'achèvement", f"{taux_achevement:.0f}%")
    
    # c) Couple SASA
    sasacouple_count = (filtered_participation["Statut_group"] == 1.0).sum()
    with col5a:
        styled_metric("Couple SASA", int(sasacouple_count))
    # c) Eyap fille
    eyapfille_count = (filtered_participation["Statut_group"] == 2.0).sum()
    with col5b:
        styled_metric("Eyap Filles", int(eyapfille_count))
    # c) Couple SASA
    eyap_garcon_count = (filtered_participation["Statut_group"] == 3.0).sum()
    with col5c:
        styled_metric("Eyap Garcons", int(eyap_garcon_count))
    # c) Couple SASA
    club_jeune_count = (filtered_participation["Statut_group"] == 4.0).sum()
    with col5d:
        styled_metric("Club des jeunes", int(club_jeune_count))

    ###############################
    

  # Création du graphique
    st.subheader("Évolution des effectifs au cours du temps")
    
    # Agrégation des données par période (exemple : par mois)
    filtered_participation["time"] = pd.to_datetime(filtered_participation["time"], errors="coerce")
    timeline_data = filtered_participation.groupby(filtered_participation["time"].dt.to_period("M")).agg({
        "Information_groupe/Effectif_debut": "sum",
        "Information_groupe/Effectif_fin": "sum"
    }).reset_index()

    # Conversion de la colonne 'time' pour Plotly
    timeline_data["time"] = timeline_data["time"].astype(str)

    # Création du graphique avec Plotly
    fig = go.Figure()

    # Ligne pour l'effectif début
    fig.add_trace(go.Scatter(
        x=timeline_data["time"],
        y=timeline_data["Information_groupe/Effectif_debut"],
        mode="lines+markers+text",
        name="Effectif début",
        line=dict(color="blue", width=3),
        marker=dict(size=8)
    ))

    # Ligne pour l'effectif fin
    fig.add_trace(go.Scatter(
        x=timeline_data["time"],
        y=timeline_data["Information_groupe/Effectif_fin"],
        mode="lines+markers+text",
        name="Effectif fin",
        line=dict(color="green", width=3),
        marker=dict(size=8)
    ))

    # Configuration du layout
    fig.update_layout(
        title="Évolution des effectifs début et fin de cursus",
        xaxis_title="Temps (par mois)",
        yaxis_title="Effectifs",
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Affichage du graphique
    st.plotly_chart(fig, use_container_width=True)

# 2. Information sur l'utilisation des services curatifs
if "ADJ" in organisation or "CARE" in organisation:
    st.header("2. Information sur l'utilisation des services curatifs")

    col5, col6, col7, col8 = st.columns(4)

    # Calculs pour les catégories d'âge
    moins_de_15 = filtered_data["totalcaseE/Feminin_caseE"].sum() + filtered_data["totalcaseE/Masculin_caseE"].sum()
    plus_15_18 = filtered_data["totalcaseI/Feminin_caseI"].sum() + filtered_data["totalcaseI/Masculin_caseI"].sum()
    plus_18_24 = filtered_data["totalcaseM/Feminin_caseM"].sum() + filtered_data["totalcaseM/Masculin_caseM"].sum() + filtered_data["totalcaseQ/Feminin_caseQ"].sum()+ filtered_data["totalcaseQ/Masculin_caseQ"].sum()
    plus_50 = filtered_data["totalcase/Feminin_case"].sum() + filtered_data["totalcase/Masculin_case"].sum()+ filtered_data["totalcaseA/Feminin_caseA"].sum()+ filtered_data["totalcaseA/Masculin_caseA"].sum()

    # Affichage des métriques
    with col5:
        styled_metric("Cas - Moins de 15 ans", int(moins_de_15))
    with col6:
        styled_metric("Cas - 15 à 18 ans", int(plus_15_18))
    with col7:
        styled_metric("Cas - 18 à 24 ans", int(plus_18_24))
    with col8:
        styled_metric("Cas - Plus de 50 ans", int(plus_50))
#3333333333333333333333333333333333333333333333333333333
# Préparation des données pour le graphique
    timeline_data = filtered_data[["time"]].copy()
    timeline_data["Moins de 15 ans"] = moins_de_15
    timeline_data["15 à 18 ans"] = plus_15_18
    timeline_data["18 à 24 ans"] = plus_18_24
    timeline_data["Plus de 50 ans"] = plus_50

    # Création du graphique avec Plotly (barres empilées)
    fig = go.Figure()

    # Ajout de chaque catégorie comme une barre empilée
    for category, color in zip(
        ["Moins de 15 ans", "15 à 18 ans", "18 à 24 ans", "Plus de 50 ans"],
        ["#636EFA", "#EF553B", "#00CC96", "#AB63FA"]
    ):
        fig.add_trace(go.Bar(
            x=timeline_data["time"],
            y=timeline_data[category],
            name=category,
            marker_color=color,
            text=timeline_data[category],  # Valeurs affichées
            textposition="inside",  # Position des valeurs à l'intérieur des barres
            hoverinfo="x+y+name"
        ))

    # Configuration du layout
    fig.update_layout(
        title="Évolution des cas par tranche d'âge",
        xaxis_title="Periode de mise en oeuvre du projet TUMA +",
        yaxis_title="Nombre de cas",
        barmode="stack",  # Barres empilées
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Affichage du graphique
    st.plotly_chart(fig, use_container_width=True)
# 3. CAS de VBG
if "ADJ" in organisation or "CARE" in organisation:
    st.header("3. Violences sexuelles et basées sur le genre")

    col9, col10, col11, col12 = st.columns(4)

    # Calculs pour les catégories d'âge
    tot_svs = filtered_data["VBG/casSVS"].sum()
    svs_fem = filtered_data["VBG/SVSFeminin"].sum()
    new_svs = filtered_data["VBG/NewSVS"].sum()
    anciensCas = filtered_data["VBG/Ancien_SVS_contre"].sum()

    # Affichage des métriques
    with col9:
        styled_metric("Nouveaux cas/SVS", int(tot_svs))
    with col10:
        styled_metric("Cas SVS Feminin", int(svs_fem))
    with col11:
        styled_metric("Nouveaux SVS", int(new_svs))
    with col12:
        styled_metric("Anciens Cas contre refere", int(anciensCas))

    # Graphique de progression
    st.subheader("Évolution des cas de VBG au fil du temps")

    # Vérification des colonnes nécessaires
    filtered_data["time"] = pd.to_datetime(filtered_data["time"], errors="coerce")  # Conversion au format datetime
    progression_data = (
        filtered_data.groupby(filtered_data["time"].dt.to_period("M"))
        .agg({
            "VBG/casSVS": "sum",
            "VBG/SVSFeminin": "sum",
            "VBG/NewSVS": "sum",
            "VBG/Ancien_SVS_contre": "sum"
        })
        .reset_index()
    )

    # Conversion de la colonne 'time' pour l'affichage
    progression_data["time"] = progression_data["time"].astype(str)

    # Création du graphique
    fig = go.Figure()

    # Ajout des séries pour chaque catégorie
    fig.add_trace(go.Scatter(
        x=progression_data["time"],
        y=progression_data["VBG/casSVS"],
        mode="lines+markers",
        name="Total cas SVS",
        line=dict(color="blue", width=2),
        marker=dict(size=6)
    ))
    fig.add_trace(go.Scatter(
        x=progression_data["time"],
        y=progression_data["VBG/SVSFeminin"],
        mode="lines+markers",
        name="Cas SVS Feminin",
        line=dict(color="purple", width=2),
        marker=dict(size=6)
    ))
    fig.add_trace(go.Scatter(
        x=progression_data["time"],
        y=progression_data["VBG/NewSVS"],
        mode="lines+markers",
        name="Nouveaux SVS",
        line=dict(color="green", width=2),
        marker=dict(size=6)
    ))
    fig.add_trace(go.Scatter(
        x=progression_data["time"],
        y=progression_data["VBG/Ancien_SVS_contre"],
        mode="lines+markers",
        name="Anciens Cas",
        line=dict(color="red", width=2),
        marker=dict(size=6)
    ))

    # Mise en forme du graphique
    fig.update_layout(
        title="Progression des cas de VBG par période",
        xaxis_title="Période",
        yaxis_title="Nombre de cas",
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Affichage du graphique
    st.plotly_chart(fig, use_container_width=True)

# 4. Santé de la mère
if "ADJ" in organisation or "CARE" in organisation:
    st.header("4. Santé de la mère, Accouchements et naissances")

    col13, col14, col15, col16, col17 = st.columns(5)

    # Calculs pour les catégories d'indicateurs
    cpn1 = filtered_data["CPN/CPN1"].sum()
    cpn4 = filtered_data["CPN/CPN4"].sum()
    Accouch = filtered_data["accouchement_naissance/accouchement1"].sum()
    Accouch20ans = filtered_data["accouchement_naissance/accouchement3"].sum()
    naiss = filtered_data["accouchement_naissance/accouchement6"].sum()

    # Affichage des métriques
    with col13:
        styled_metric("Total CPN1", int(cpn1))
    with col14:
        styled_metric("Total CPN4", int(cpn4))
    with col15:
        styled_metric("Accouchements", int(Accouch))
    with col16:
        styled_metric("Accouchements - 20ans", int(Accouch20ans))
    with col17:
        styled_metric("Naissances vivantes", int(naiss))

    # Graphique amélioré
    st.subheader("Progression des indicateurs de santé maternelle au fil du temps")

    # Vérification des colonnes nécessaires
    filtered_data["time"] = pd.to_datetime(filtered_data["time"], errors="coerce")  # Conversion au format datetime
    progression_data = (
        filtered_data.groupby(filtered_data["time"].dt.to_period("M"))
        .agg({
            "CPN/CPN1": "sum",
            "CPN/CPN4": "sum",
            "accouchement_naissance/accouchement1": "sum",
            "accouchement_naissance/accouchement3": "sum",
            "accouchement_naissance/accouchement6": "sum"
        })
        .reset_index()
    )

    # Conversion de la colonne 'time' pour l'affichage
    progression_data["time"] = progression_data["time"].astype(str)

    # Création du graphique amélioré
    fig = go.Figure()

    # Ajout des barres pour chaque indicateur avec des légendes
    indicators = {
        "CPN/CPN1": {"name": "Total CPN1", "color": "blue"},
        "CPN/CPN4": {"name": "Total CPN4", "color": "purple"},
        "accouchement_naissance/accouchement1": {"name": "Accouchements", "color": "green"},
        "accouchement_naissance/accouchement3": {"name": "Accouchements - 20ans", "color": "orange"},
        "accouchement_naissance/accouchement6": {"name": "Naissances vivantes", "color": "red"},
    }

    for column, props in indicators.items():
        fig.add_trace(go.Bar(
            x=progression_data["time"],
            y=progression_data[column],
            name=props["name"],
            text=progression_data[column],  # Ajout des valeurs sur les barres
            textposition="outside",  # Position des valeurs en haut des barres
            marker_color=props["color"]
        ))

    # Mise en forme du graphique
    fig.update_layout(
        xaxis_title="Période",
        yaxis_title="Nombre de cas",
        barmode="group",  # Regroupement des barres par période
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        height=600,
    )

    # Style des axes
    fig.update_xaxes(
        tickangle=-45,  # Orientation des étiquettes de l'axe X
        showgrid=False
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="lightgrey"
    )

    # Affichage du graphique
    st.plotly_chart(fig, use_container_width=True)

#33######fin4#################################
# 5. Santé de la mère
if "ADJ" in organisation or "CARE" in organisation:
    st.header("5. Décès liés à l'accouchement")

    col18, col19, col20, col21 = st.columns(4)

    # Calculs pour les catégories
    dec1 = filtered_data["deces_accouchements/deces_nouv1"].sum()
    dec2 = filtered_data["deces_accouchements/deces_nouv2"].sum()
    dec3 = filtered_data["deces_accouchements/deces_nouv3"].sum()
    dec4 = filtered_data["deces_accouchements/deces_nouv4"].sum()

    # Affichage des métriques
    with col18:
        styled_metric("Décès nouveaux-nés de -7 jours", int(dec1))
    with col19:
        styled_metric("Décès nouveaux-nés de -28 jours", int(dec2))
    with col20:
        styled_metric("Décès maternels", int(dec3))
    with col21:
        styled_metric("Décès maternels revus", int(dec4))

    # Préparation des données pour le graphique
    st.subheader("Évolution des décès liés à l'accouchement par période")

    filtered_data["time"] = pd.to_datetime(filtered_data["time"], errors="coerce")  # Conversion au format datetime
    progression_data = (
        filtered_data.groupby(filtered_data["time"].dt.to_period("M"))
        .agg({
            "deces_accouchements/deces_nouv1": "sum",
            "deces_accouchements/deces_nouv2": "sum",
            "deces_accouchements/deces_nouv3": "sum",
            "deces_accouchements/deces_nouv4": "sum",
        })
        .reset_index()
    )

    # Conversion de la colonne 'time' pour l'affichage
    progression_data["time"] = progression_data["time"].astype(str)

    # Création du graphique linéaire
    fig = go.Figure()

    # Ajouter les catégories au graphique
    categories = {
        "deces_accouchements/deces_nouv1": "Décès nouveaux-nés de -7 jours",
        "deces_accouchements/deces_nouv2": "Décès nouveaux-nés de -28 jours",
        "deces_accouchements/deces_nouv3": "Décès maternels",
        "deces_accouchements/deces_nouv4": "Décès maternels revus",
    }
    colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA"]

    for i, (column, name) in enumerate(categories.items()):
        fig.add_trace(go.Scatter(
            x=progression_data["time"],
            y=progression_data[column],
            mode="lines+markers",  # Lignes avec points
            name=name,
            line=dict(color=colors[i], width=2),
            marker=dict(size=6)
        ))

    # Mise en forme du graphique
    fig.update_layout(
        xaxis_title="Période",
        yaxis_title="Nombre de décès",
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        height=600,
    )

    # Ajout du style des axes
    fig.update_xaxes(
        tickangle=-45,
        showgrid=False
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="lightgrey"
    )

    # Affichage du graphique
    st.plotly_chart(fig, use_container_width=True)

# 6. Acceptentes
if "ADJ" in organisation or "CARE" in organisation:
    st.header("6. Informations sur les acceptantes des methodes de la planification familiale")

    col22, col23, col24, col25, col26, col27 = st.columns(6)

    # Calculs pour les catégories d'âge
    dec11 = filtered_data["acceptante/Nvlle_acceptante_meth/Nbre_Fosa"].sum()
    dec12 = filtered_data["acceptante/Nvlle_acceptante_meth/Nbre_adbc"].sum()
    dec13 = filtered_data["acceptante/Nvlles_aceptante_moins18/Nbre_Fosa2"].sum()
    dec14 = filtered_data["acceptante/Nvlles_aceptante_moins18/Nbre_adbc2"].sum()
    dec15 = filtered_data["acceptante/Nvlle_acceptante_18_24/Nbre_Fosa1"].sum()
    dec16 = filtered_data["acceptante/Nvlle_acceptante_18_24/Nbre_adbc1"].sum()

    # Affichage des métriques
    with col22:
        styled_metric("Nouvelles acceptentes des methodes de PF aux FOSA", int(dec11))
    with col23:
        styled_metric("Nouvelles acceptentes des methodes de PF à l'ADBC", int(dec12))
    with col24:
        styled_metric("Acceptentes des methodes de PF aux FOSA de -18 ans", int(dec13))
    with col25:
        styled_metric("Acceptentes des methodes de PF à l'ADBC de -18 ans", int(dec14))
    with col26:
        styled_metric("Acceptentes des methodes de PF aux FOSA de 18-24 ans", int(dec15))
    with col27:
        styled_metric("Acceptentes des methodes de PF a l'ADBC de 18-24 ans", int(dec16))
 
 # Seconde ligne de visuels
    st.write("")  # Espacement entre les lignes
    col28, col29, col30, col31, col32, col33 = st.columns(6)

    # Calculs pour les catégories supplémentaires (seconde ligne)
    dec17 = filtered_data["acceptante/Renouvellement_Planification_familiale/Nbre_Fosa5"].sum()
    dec18 = filtered_data["acceptante/Renouvellement_Planification_familiale/Nbre_adbc5"].sum()
    dec19 = filtered_data["acceptante/Nvelles_acceptantes_post_avortemt/Nbre_Fosa6"].sum()
    dec20 = filtered_data["acceptante/Nvelles_acceptantes_post_avortemt/Nbre_adbc6"].sum()
    dec21 = filtered_data["acceptante/Nbre_beneficiaires_SCACF/Nbre_Fosa7"].sum()
    dec22 = filtered_data["acceptante/Nbre_beneficiaires_SCACF/Nbre_adbc7"].sum()

    # Affichage des métriques pour la seconde ligne
    with col28:
        styled_metric("Renouvellement planification familiale FOSA", int(dec17))
    with col29:
        styled_metric("Renouvellement planification familiale ADBC", int(dec18))
    with col30:
        styled_metric("Nvelles acceptantes des soins après avortement FOSA", int(dec19))
    with col31:
        styled_metric("Nvelles acceptantes des soins après avortement ADBC", int(dec20))
    with col32:
        styled_metric("Beneficiares SCACF/soins complets d'avort centrés sur la femme FOSA", int(dec21))
    with col33:
        styled_metric("Beneficiares SCACF/soins complets d'avort centrés sur la femme ADBC", int(dec22))

# Préparation des données temporelles avec des noms significatifs pour les acceptantes
if "ADJ" in organisation or "CARE" in organisation:
    # Dictionnaire des descriptions pour les colonnes
    column_descriptions = {
        "Nvlle_acceptante_meth/Nbre_Fosa": "Nouvelles acceptantes - Méthodes PF aux FOSA",
        "Nvlle_acceptante_meth/Nbre_adbc": "Nouvelles acceptantes - Méthodes PF à l'ADBC",
        "Nvlles_aceptante_moins18/Nbre_Fosa2": "Acceptantes de moins de 18 ans - FOSA",
        "Nvlles_aceptante_moins18/Nbre_adbc2": "Acceptantes de moins de 18 ans - ADBC",
        "Nvlle_acceptante_18_24/Nbre_Fosa1": "Acceptantes de 18 à 24 ans - FOSA",
        "Nvlle_acceptante_18_24/Nbre_adbc1": "Acceptantes de 18 à 24 ans - ADBC",
        "Renouvellement_Planification_familiale/Nbre_Fosa5": "Renouvellement PF - FOSA",
        "Renouvellement_Planification_familiale/Nbre_adbc5": "Renouvellement PF - ADBC",
        "Nvelles_acceptantes_post_avortemt/Nbre_Fosa6": "Acceptantes après avortement - FOSA",
        "Nvelles_acceptantes_post_avortemt/Nbre_adbc6": "Acceptantes après avortement - ADBC",
        "Nbre_beneficiaires_SCACF/Nbre_Fosa7": "Bénéficiaires SCACF - FOSA",
        "Nbre_beneficiaires_SCACF/Nbre_adbc7": "Bénéficiaires SCACF - ADBC",
    }

    # Ajout des colonnes nécessaires pour l'analyse temporelle
    categories = list(column_descriptions.keys())
    time_series_data = filtered_data[["time"] + [f"acceptante/{cat}" for cat in categories]].copy()

    # Mise en forme longue des données
    time_series_data = time_series_data.melt(
        id_vars=["time"],
        var_name="Categorie",
        value_name="Valeur",
    )
    time_series_data["Categorie"] = time_series_data["Categorie"].str.replace("acceptante/", "", regex=False)
    time_series_data["Categorie"] = time_series_data["Categorie"].map(column_descriptions)
    time_series_data["time"] = pd.to_datetime(time_series_data["time"])

    # Agrégation des données par date et catégorie
    time_series_summary = time_series_data.groupby(["time", "Categorie"])["Valeur"].sum().reset_index()

    # Création du graphique interactif
    fig = px.line(
        time_series_summary,
        x="time",
        y="Valeur",
        color="Categorie",
        title="Évolution des acceptantes des méthodes de planification familiale dans le temps",
        labels={"time": "Date", "Valeur": "Nombre Total", "Categorie": "Catégories"},
        line_shape="spline",
    )
    fig.update_layout(
        height=600,
        legend_title="Catégories",
        xaxis_title="Date",
        yaxis_title="Nombre Total",
    )
    st.plotly_chart(fig)

###########################################################
# 7. Communication
if "ADJ" in organisation or "CARE" in organisation:
    st.header("7. Communication sur le changement de comportement (CCC)")

    col34, col35, col36, col37, col38, col39, col40, col41, col42 = st.columns(9)

    # Calculs pour les catégories
    ccc1 = filtered_data["communication_changement_comportement/seances_prevues"].sum()
    ccc2 = filtered_data["communication_changement_comportement/seances_realises"].sum()
    ccc3 = filtered_data["communication_changement_comportement/participants_hommes"].sum()
    ccc4 = filtered_data["communication_changement_comportement/participants_femmes"].sum()
    ccc5 = filtered_data["communication_changement_comportement/participants_jeunes_filles"].sum()
    ccc6 = filtered_data["communication_changement_comportement/participants_jeunes_garcons"].sum()
    ccc7 = filtered_data["communication_changement_comportement/participants_adolescentes_filles"].sum()
    ccc8 = filtered_data["communication_changement_comportement/participants_adolescentes_garcons"].sum()
    ccc9 = filtered_data["communication_changement_comportement/participants_referes_fosa"].sum()

    # Affichage des métriques
    with col34:
        styled_metric("Séances prévues", int(ccc1))
    with col35:
        styled_metric("Séances réalisées", int(ccc2))
    with col36:
        styled_metric("Participants hommes", int(ccc3))
    with col37:
        styled_metric("Participants femmes", int(ccc4))
    with col38:
        styled_metric("Participants filles", int(ccc5))
    with col39:
        styled_metric("Participants garçons", int(ccc6))
    with col40:
        styled_metric("Partic adolescentes", int(ccc7))
    with col41:
        styled_metric("Partic adolescents", int(ccc8))
    with col42:
        styled_metric("Partic référés FOSA", int(ccc9))

    # Préparer les données pour le graphique
    filtered_data['time'] = pd.to_datetime(filtered_data['time'])  # Conversion à datetime

    # Convertir les colonnes en numériques pour éviter les erreurs
    numeric_columns = [
        "communication_changement_comportement/seances_prevues",
        "communication_changement_comportement/seances_realises",
        "communication_changement_comportement/participants_hommes",
        "communication_changement_comportement/participants_femmes",
    ]
    filtered_data[numeric_columns] = filtered_data[numeric_columns].apply(pd.to_numeric, errors='coerce')

    # Grouper les données par mois et additionner les valeurs
    grouped_data = (
        filtered_data.groupby(filtered_data['time'].dt.to_period('M'))[numeric_columns]
        .sum()
        .reset_index()
    )
    grouped_data['time'] = grouped_data['time'].astype(str)  # Conversion pour l'affichage

    # Colonnes pour le graphique
    columns_to_plot = numeric_columns
    legend_names = [
        "Séances prévues",
        "Séances réalisées",
        "Participants hommes",
        "Participants femmes",
    ]
    colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA"]

    # Création du graphique
    fig = go.Figure()

    for i, column in enumerate(columns_to_plot):
        fig.add_trace(go.Bar(
            x=grouped_data['time'],
            y=grouped_data[column],
            name=legend_names[i],
            marker=dict(color=colors[i])
        ))

    # Mise en forme du graphique
    fig.update_layout(
        title="Évolution CCC",
        xaxis_title="Période",
        yaxis_title="Valeurs",
        barmode="group",  # Histogrammes groupés
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        height=600,
    )

    # Ajout du style des axes
    fig.update_xaxes(tickangle=-45, showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="lightgrey")

    # Affichage du graphique
    st.plotly_chart(fig, use_container_width=True)

#########################################################TRANSMISSINLE###############################
# 8. IST
if "ADJ" in organisation or "CARE" in organisation:
    st.header("8. Informations sur les maladies transmissibles")
    st.subheader("1. IST Nouveaux cas")


    col43, col44, col45, col46, col47, col48, col49 = st.columns(7)

    # Calculs pour les catégories d'âge
    ist1 = filtered_data["IST/Nouv_feminY7/infer15Y7"].sum()
    ist2 = filtered_data["IST/Nouv_feminY7/quinze_24Y7"].sum()
    ist3 = filtered_data["IST/Nouv_feminY7/Vingt5Y7"].sum()
    ist4 = filtered_data["IST/Nouv_feminZ/infer15YZ"].sum()
    ist5 = filtered_data["IST/Nouv_feminZ/quinze_24YZ"].sum()
    ist6 = filtered_data["IST/Nouv_feminZ/Vingt5YZ"].sum()
    ist7 = filtered_data["IST/Nouv_feminZ/TotNouvCaseM"].sum() + filtered_data["IST/Nouv_feminY7/TotNouvCaseF"].sum()


    # Affichage des métriques
    with col43:
        styled_metric("Feminin : <15 ans", int(ist1))
    with col44:
        styled_metric("Feminin : 15-24 ans", int(ist2))
    with col45:
        styled_metric("Feminin : >25 ans", int(ist3))
    with col46:
        styled_metric("Masculin : <15 ans", int(ist4))
    with col47:
        styled_metric("Masculin : 15-24 ans", int(ist5))
    with col48:
        styled_metric("Masculin : >25 ans", int(ist6))
    with col49:
        styled_metric("Total", int(ist7))
    
    

    st.subheader("2. Cas contact parmi les nouveaux cas")


    col50, col51, col52, col53, col54, col55, col56 = st.columns(7)

    # Calculs pour les catégories d'âge
    ist1 = filtered_data["IST/Nouv_femin/infer15"].sum()
    ist2 = filtered_data["IST/Nouv_femin/quinze_24"].sum()
    ist3 = filtered_data["IST/Nouv_femin/Vingt5"].sum()
    ist4 = filtered_data["IST/Nouv_garc/infer151"].sum()
    ist5 = filtered_data["IST/Nouv_garc/quinze_241"].sum()
    ist6 = filtered_data["IST/Nouv_garc/Vingt51"].sum()
    ist7 = filtered_data["IST/Nouv_femin/TotalCasContactIST_F"].sum() + filtered_data["IST/Nouv_garc/TotalCasContactIST_M"].sum()


    # Affichage des métriques
    with col50:
        styled_metric("Feminin : <15 ans", int(ist1))
    with col51:
        styled_metric("Feminin : 15-24 ans", int(ist2))
    with col52:
        styled_metric("Feminin : >25 ans", int(ist3))
    with col53:
        styled_metric("Masculin : <15 ans", int(ist4))
    with col54:
        styled_metric("Masculin : 15-24 ans", int(ist5))
    with col55:
        styled_metric("Masculin : >25 ans", int(ist6))
    with col56:
        styled_metric("Total", int(ist7))
    
    st.subheader("3. Traites selon l'approche syndromique")


    col57, col58, col59, col60, col61, col62, col63 = st.columns(7)

    # Calculs pour les catégories d'âge
    iist1 = filtered_data["IST/contacts_new_case1/infer154"].sum()
    iist2 = filtered_data["IST/contacts_new_case1/quinze_244"].sum()
    iist3 = filtered_data["IST/contacts_new_case1/Vingt54"].sum()
    iist4 = filtered_data["IST/contacts_new_case/infer153"].sum()
    iist5 = filtered_data["IST/contacts_new_case/quinze_243"].sum()
    iist6 = filtered_data["IST/contacts_new_case/Vingt53"].sum()
    iist7 = filtered_data["IST/contacts_new_case1/totalCasTraiteSyndromeF"].sum() + filtered_data["IST/contacts_new_case/totalCasTraiteSyndromeM"].sum()


    # Affichage des métriques
    with col57:
        styled_metric("Feminin : <15 ans", int(iist1))
    with col58:
        styled_metric("Feminin : 15-24 ans", int(iist2))
    with col59:
        styled_metric("Feminin : >25 ans", int(iist3))
    with col60:
        styled_metric("Masculin : <15 ans", int(iist4))
    with col61:
        styled_metric("Masculin : 15-24 ans", int(iist5))
    with col62:
        styled_metric("Masculin : >25 ans", int(iist6))
    with col63:
        styled_metric("Total", int(iist7))
    
    st.subheader("4. Traites selon l'approche etiologique")


    col64, col65, col66, col67, col68, col69, col70 = st.columns(7)

    # Calculs pour les catégories d'âge
    ist1 = filtered_data["IST/contacts_new_caseY/infer153L"].sum()
    ist2 = filtered_data["IST/contacts_new_caseY/quinze_243L"].sum()
    ist3 = filtered_data["IST/contacts_new_caseY/Vingt53L"].sum()
    ist4 = filtered_data["IST/contacts_new_caseR/infer153R"].sum()
    ist5 = filtered_data["IST/contacts_new_caseR/quinze_243R"].sum()
    ist6 = filtered_data["IST/contacts_new_caseR/Vingt53R"].sum()
    ist7 = filtered_data["IST/contacts_new_caseY/overall3L"].sum() + filtered_data["IST/contacts_new_caseR/overall3R"].sum()


    # Affichage des métriques
    with col64:
        styled_metric("Feminin : <15 ans", int(ist1))
    with col65:
        styled_metric("Feminin : 15-24 ans", int(ist2))
    with col66:
        styled_metric("Feminin : >25 ans", int(ist3))
    with col67:
        styled_metric("Masculin : <15 ans", int(ist4))
    with col68:
        styled_metric("Masculin : 15-24 ans", int(ist5))
    with col69:
        styled_metric("Masculin : >25 ans", int(ist6))
    with col70:
        styled_metric("Total", int(ist7))
    
###
# Affichage des métriques pour les catégories d'âge



st.header("FILTREZ POUR VOIR LES DONNEES INTERACTIVES")
st.subheader("Indicator of progress !!!! En cours de traitement, ces indicateurs viseront a voir l'atteinte des resultats ")

