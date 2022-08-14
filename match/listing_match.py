import sys
import traceback
import pandas as pd
from match import graphql
from fuzzywuzzy import fuzz
from unidecode import unidecode


def match_graphql(name, near):
    """
    Search the listing id info through region_locality.
    :param name:(str).
    :param near:(str) one of the postcode, location, region_locality
    :return result_df:(df) columns such as ['score', 'id', 'name', 'otherNames', 'street', 'locality', 'region',
                               'postalCode', 'primaryLink', 'email', 'category', 'denomination', 'type']
    :return top_score:(int) If graphql find nothing, it will return 0.
    :return result_num:(int) If graphql find nothing, it will return 0.
    """
    result_df = pd.DataFrame(columns=['score', 'id', 'name', 'otherNames', 'street', 'locality', 'region',
                                      'postalCode', 'primaryLink', 'email', 'category', 'denomination', 'type'])
    search_params = {"keywords": name, "near": near}
    graphql_df = graphql.listingsearch(**search_params)  # df or list
    if len(graphql_df) > 0:
        top_score = graphql_df['score'].max()
        result_num = len(graphql_df)
        result_df = graphql_df.sort_values('score', ascending=False)
        result_df.reset_index(drop=True, inplace=True)
        return result_df, top_score, result_num
    else:
        return result_df, 0, 0


def other_name_list(name_list):
    """
    Extract the other_name as one list from the df.
    :param name_list: (list) The other name data from the df.
    Such as [['BN: 139138861RR0002', 'THE CENTRAL CANADIAN DISTRICT OF THE CHRISTIAN AND MISSIONARY ALLIANCE IN CANADA']]
    :return result_list: (list) Only include the list of other name or [].
    Such as ['THE CENTRAL CANADIAN DISTRICT OF THE CHRISTIAN AND MISSIONARY ALLIANCE IN CANADA']
    """
    result_list = []
    if len(name_list) > 0:
        for i in name_list:
            if isinstance(i, list) and len(i) > 1:
                for j in i[1:]:
                    result_list.append(j)
    return result_list


def name_similarity(name, df, near_type, pst_threshold, region_threshold):
    """
    Using Levenshtein Distance algorithm. Compare input name to the fist row's item in the input df .
    :param name:(str) Such as "The Metropolitan Bible Church".
    :param df:(df) Must include "name" column.
    :param near_type:(str) Only three types, as "postcode" or "location" or "region_locality".
    :param pst_threshold:(int) It is set from main().
    :param region_threshold:(int) It is set from main().
    :return score :(int or None)
    """
    name = unidecode(name.lower())
    name_list = df['name'].values.tolist()
    if 'otherNames' in df.columns:
        oth_name_list = other_name_list(df['otherNames'].values.tolist())
        name_list = name_list + oth_name_list
    score = max([fuzz.partial_ratio(name, i.lower()) for i in name_list])
    if near_type == 'postcode' or near_type == 'location':
        return score if score > pst_threshold else None
    if near_type == 'region_locality':
        return score if score > region_threshold + 20 else None


def filter_multi_result(df, epsilon):
    """
    This section is to deal with cases with multiple results.
    :param df:(df) This is source from graphql
    :param epsilon:(int) Set in the main()
    :return id:(str)  name:(str)   score:(int)  or None  notes:(str)
    """
    if len(df) == 2:
        if (df.loc[0].score - df.loc[1].score) > epsilon:
            return df.loc[0]['id'], df.loc[0]['name'], df.loc[0]['score']
        else:
            notes = "Failure: Multiple possible top results, but less than epsilon"
            return None, notes
    else:
        if (df.loc[0].score - df.loc[1].score) > (df.loc[1].score - df.loc[2].score):
            return df.loc[0]['id'], df.loc[0]['name'], df.loc[0]['otherNames'], df.loc[0]['score']
        else:
            notes = "Failure: Multiple possible top results, but top two are two good results"
            return None, notes


def main(name, postcode='', address='', region_locality='', epsilon=5, pst_threshold=60, region_threshold=80):
    """
    Main program.
    :param name:(str)
    :param postcode:(str)
    :param address:(str)
    :param region_locality:(str)
    :param epsilon:(int) Default is 5.
    :param pst_threshold:(int) It be used to judge whether the score using postcode or location is good. Default is 60.
    :param region_threshold:(int) It be used to judge whether the score using region is good. Default is 80.
    :return result_list:(list) ['id', 'graphql_score', 'text_score, 'near_type', 'notes']
    """
    notes = "Failure: Graphql response nothing."
    result_list = ['', 0, 0, '', notes]
    loc_list = [['postcode', postcode], ['location', address+','+region_locality], ['region_locality', region_locality]]
    for near_type, near in loc_list:
        if near == '':
            continue
        else:
            df, top_score, number = match_graphql(name, near)
            if number == 1:
                text_score = name_similarity(name, df, near_type, pst_threshold, region_threshold)
                if text_score is not None:
                    notes = "Success: Sole area-based result."
                    result_list = [df['id'][0], df['score'][0], text_score, near_type, notes]
                    break
                else:
                    notes = "Failure: text_score is slow"
                    continue
            if number > 1:
                filter_set = filter_multi_result(df, epsilon)
                if filter_set[0] is None and filter_set[1] != '':
                    # have a failure result
                    continue
                else:
                    # have a good result, continue to text match
                    df_temp = pd.DataFrame({'name': [filter_set[1]], 'otherNames': [filter_set[2]]})
                    text_score = name_similarity(name, df_temp, near_type, pst_threshold, region_threshold)
                    if text_score is not None:
                        notes = "Success: Multiple results and top one matched."
                        result_list = [df['id'][0], df['score'][0], text_score, near_type, notes]
                        break
                    else:
                        continue
    if result_list[0] == '':
        result_list = ['', 0, 0, '', notes]
    return result_list


if __name__ == '__main__':
    # my_name = "The Metropolitan Bible Church"
    # my_location = "2176 Prince of Wales Dr,Ottawa,Ontario,K2E 0A1"
    # my_postcode = "K2E 0A1"
    # my_address = "2176 Prince of Wales Dr"
    # my_region_locality = "Ottawa,Ontario"

    my_name = "The Central Canadian District of the Christian and Missionary Alliance in Canada"
    my_location = "159 Panin Road,Burlington,Ontario,L7P 5A6"
    my_postcode = "L7P 5A6"
    my_address = "159 Panin Road"
    my_region_locality = "Burlington,Ontario"

    # my_name = "Tyndale University"
    # my_postcode = "M2M 3S4"
    # my_address = "3377 Bayview Ave,Toronto"
    # my_region_locality = "Toronto,Ontario"

    response = main(my_name, my_postcode, my_address, my_region_locality)
    print(f"response is :\n{response}")
