import uvicorn
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from match import listing_match
app = FastAPI()


class Item(BaseModel):
    name: str
    postcode: Optional[str] = None
    address: Optional[str] = None
    region_locality: Optional[str] = None


@app.post('/listings/matching/')
async def update_item(item: Item):
    postcode = (item.postcode and item.postcode or '')
    address = (item.address and item.address or '')
    region_locality = (item.region_locality and item.region_locality or '')
    response = listing_match.main(item.name, postcode, address, region_locality)
    result = {
        "listingId": response[0],
        "score": response[1],
        "textMatch": response[2],
        "near": response[3],
        "notes": response[4]
    }
    if len(response) > 0:
        results = {
            "results": result
        }
    else:
        results = {
            "results": "Nothing."
        }
    return results


@app.get('/')
def read_root():
    return {"Hello": "World, da-services"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=80)
