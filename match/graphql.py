import requests
import time
import json
import pandas as pd
import settings


def listingsearch(keywords,near=""):
    gqlvar = locals()
    # search for boundary to define relevant listings
        # if no location provided it takes the entire boundary based on keyword
        # results
    locquery = """
        query SearchViewportQuery(
            $keywords: String            
            $near: String            
        ) {
            search(keywords: $keywords)                
                {                
                viewport(near: $near) {
                    bounds
                    coordinates
                }
            }
        }
        """
    for attempt in range(4):
        locr = requests.post(settings.API_URL, json={'query': locquery, 'variables': gqlvar})
        try:
            # take viewport for main query
            gqlvar['viewport'] = (json.loads(locr.text)['data']['search']['viewport']['bounds'])
        except:
            time.sleep(3)  # pause if problem with results and retry
        else:
            break  # continue if expected results received
    else:
        locr = requests.post(settings.API_URL,
                             json={'query': locquery, 'variables': {"keywords": keywords, "near": ""}})
        gqlvar['viewport'] = (json.loads(locr.text)['data']['search']['viewport']['bounds'])

    query = """
            query SearchQuery(
                $keywords: String
                $viewport: BoundsInput!                        
                ){
                search(
                    keywords: $keywords
                    types: [listing]                
                ){                
                    results(                    
                        sort: {
                            field: score
                            direction: desc
                        }
                        viewport: $viewport
                    ) {
                        edges {
                            _meta {
                                score
                            }
                            node {
                                id
                                ... on Listing {
                                    name
                                    otherNames                                                        
                                    location {                                    
                                        address {
                                            street
                                            locality
                                            region
                                            postalCode                                        
                                        }                                    
                                    }
                                    primaryLink
                                    email
                                    tags {
                                        category
                                        denomination
                                        type
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """
    for attempt in range(4):
        listr = requests.post(settings.API_URL, json={'query': query, 'variables': gqlvar})
        try:
            results = json.loads(listr.text)['data']['search']['results']['edges']
        except:
            time.sleep(3)  # pause if problem with results and retry
        else:
            break  # continue if expected results received
    else:
        return []

    if len(results) > 0:
        df = pd.json_normalize(results)
        # rename columns without record path
        df.columns = [c.split('.')[-1] for c in df.columns]
        return df
    else:
        return []


if __name__ == '__main__':
    pd.set_option('display.float_format', lambda x: '%.0f' % x)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    keywords = "Westside Calgary Chinese Alliance Church"
    near = "6600 Country Hills Blvd NW,Calgary"
    result_df = listingsearch(keywords, near)
    if len(result_df) > 0:
        print(result_df[0:3])
    else:
        print("nothing")
