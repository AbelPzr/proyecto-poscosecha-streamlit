import io
import pandas as pd
from scipy.stats import f_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import streamlit as st
from compactletterdisplay import compact_letter_display

def anova_test(df, group_column, target_column):

    groups = df[group_column].dropna().unique()

    data_groups = [
        df[df[group_column] == g][target_column].dropna()
        for g in groups
    ]

    f_stat, p_value = f_oneway(*data_groups)

    return {
        "f_statistic": float(f_stat),
        "p_value": float(p_value),
        "significativo": p_value < 0.05
    }


def calcular_estadisticas(df, group_column, target_column):

    stats = (
        df.groupby(group_column)[target_column]
        .agg(['mean', 'std', 'median', 'var', 'count'])
        .reset_index()
    )

    stats.columns = [
        group_column,
        "Media",
        "Desv. Estándar",
        "Mediana",
        "Varianza",
        "n"
    ]

    return stats




def tukey_hsd_test(df, group_column, target_column, alpha=0.05):

    try:

        # =====================================================
        # LIMPIEZA
        # =====================================================

        data = df[[group_column, target_column]].dropna()

        if len(data) == 0:

            return {
                "error": f"No hay datos válidos en {group_column} o {target_column}"
            }

        # =====================================================
        # MEDIAS
        # =====================================================

        means = (
            data.groupby(group_column)[target_column]
            .mean()
            .sort_values(ascending=False)
        )

        ordered_groups = means.index.tolist()

        # =====================================================
        # TUKEY
        # =====================================================

        tukey = pairwise_tukeyhsd(
            endog=data[target_column],
            groups=data[group_column],
            alpha=alpha
        )

        tukey_df = pd.DataFrame(
            data=tukey._results_table.data[1:],
            columns=tukey._results_table.data[0]
        )

        # =====================================================
        # MATRIZ DE DIFERENCIAS
        # True = diferentes
        # False = NO diferentes
        # =====================================================

        reject_matrix = pd.DataFrame(
            False,
            index=ordered_groups,
            columns=ordered_groups
        )

        for _, row in tukey_df.iterrows():

            g1 = row["group1"]
            g2 = row["group2"]

            reject_matrix.loc[g1, g2] = row["reject"]
            reject_matrix.loc[g2, g1] = row["reject"]

        # =====================================================
        # CLD
        # =====================================================

        letters = []
        group_letters = {
            g: ""
            for g in ordered_groups
        }

        current_letter = ord("a")

        for group in ordered_groups:

            assigned = False

            for letter in letters:

                compatible = True

                for other_group in ordered_groups:

                    if letter in group_letters[other_group]:

                        if reject_matrix.loc[group, other_group]:

                            compatible = False
                            break

                if compatible:

                    group_letters[group] += letter
                    assigned = True

            if not assigned:

                new_letter = chr(current_letter)

                letters.append(new_letter)

                group_letters[group] += new_letter

                current_letter += 1

        # =====================================================
        # SEGUNDA PASADA
        # =====================================================

        for g1 in ordered_groups:

            for g2 in ordered_groups:

                if g1 == g2:
                    continue

                # Tukey dice que NO son diferentes
                if not reject_matrix.loc[g1, g2]:

                    letras1 = set(group_letters[g1])
                    letras2 = set(group_letters[g2])

                    # Ya comparten letra
                    if letras1.intersection(letras2):
                        continue

                    # Buscar una letra compatible
                    for letra in letras1:

                        compatible = True

                        for other_group in ordered_groups:

                            if (
                                letra in group_letters[other_group]
                                and reject_matrix.loc[g2, other_group]
                            ):
                                compatible = False
                                break

                        if compatible:

                            group_letters[g2] += letra
                            break

        # =====================================================
        # TERCERA PASADA
        # Garantizar coherencia total
        # =====================================================

        changed = True

        while changed:

            changed = False

            for g1 in ordered_groups:

                for g2 in ordered_groups:

                    if g1 == g2:
                        continue

                    if not reject_matrix.loc[g1, g2]:

                        letras1 = set(group_letters[g1])
                        letras2 = set(group_letters[g2])

                        if len(letras1.intersection(letras2)) == 0:

                            for letra in letras1:

                                compatible = True

                                for other_group in ordered_groups:

                                    if (
                                        letra in group_letters[other_group]
                                        and reject_matrix.loc[g2, other_group]
                                    ):
                                        compatible = False
                                        break

                                if compatible:

                                    group_letters[g2] += letra
                                    changed = True
                                    break

        # =====================================================
        # LIMPIEZA
        # =====================================================

        for g in group_letters:

            group_letters[g] = "".join(
                sorted(
                    set(group_letters[g])
                )
            )

        # =====================================================
        # VALIDACIÓN
        # =====================================================

        errores = []

        for g1 in ordered_groups:

            for g2 in ordered_groups:

                if g1 == g2:
                    continue

                letras1 = set(group_letters[g1])
                letras2 = set(group_letters[g2])

                comparten = bool(
                    letras1.intersection(letras2)
                )

                if not reject_matrix.loc[g1, g2]:

                    if not comparten:

                        errores.append(
                            f"{g1} y {g2} deberían compartir letra"
                        )

                else:

                    if comparten:

                        errores.append(
                            f"{g1} y {g2} NO deberían compartir letra"
                        )

        # =====================================================
        # RESULTADO
        # =====================================================

        result_df = pd.DataFrame({

            group_column: ordered_groups,

            "Media": [
                means[g]
                for g in ordered_groups
            ],

            "Grupos": [
                group_letters[g]
                for g in ordered_groups
            ]

        })

        return {

            "resultado": result_df.reset_index(drop=True),

            "tukey": tukey_df,

            "reject_matrix": reject_matrix,

            "group_letters": group_letters,

            "errores": errores

        }

    except Exception as e:

        return {
            "error": str(e)
        }