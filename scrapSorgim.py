#%%libraries
import requests
import pandas as pd
import datetime
import time
#%%funcs
def getMarketData():
    '''
    fetches market data automatically for current date

    Returns
    -------
    resultDf : Dataframe
        productId,productName,prices,categoryId,categoryName.

    '''
    tic = time.perf_counter()
    catResponse = requests.get("https://www.migros.com.tr/rest/categories").json()
    restUrl = "https://www.migros.com.tr/rest/products/search?category-id="
    
    resultDf = pd.DataFrame(columns=["productId","productName","regularPrice","loyaltyPrice","salePrice","shownPrice",
                                     "categoryId","categoryName","subCategoryId","subCategoryName","date"])
    
    today = datetime.date.today()
    
    for i in range(len(catResponse["data"])):
        
        motherCategoryName = catResponse["data"][i]["data"]["name"]
        motherCategoryId = catResponse["data"][i]["data"]["id"]
        
        print("category : ",motherCategoryName)
        
        if(catResponse["data"][i]["children"] != list()):
            
            level1 = catResponse["data"][i]["children"]
            
            for j in range(len(level1)):
                level1CatName = level1[j]["data"]["name"]
                level1Id = level1[j]["data"]["id"]
                catUrl = restUrl+str(level1Id)
                
                productResponse = requests.get(catUrl).json()
                pageCount = productResponse["data"]["pageCount"]
                
                print("subCategory : ",level1CatName)
                print("totalPage : ",pageCount)
                
                
                for p in range(pageCount):
                    tempResponse = requests.get(catUrl+"&sayfa="+str(p+1)).json()
                    productInfo = tempResponse["data"]["storeProductInfos"]
                    
                    print("page : ",p+1)
                    
                    
                    for l in range(len(productInfo)):
                        productId = productInfo[l]["id"]
                        productName = productInfo[l]["name"]
                        
                        regularPrice = productInfo[l]["regularPrice"]/100
                        loyaltyPrice = productInfo[l]["loyaltyPrice"]/100
                        salePrice = productInfo[l]["salePrice"]/100
                        shownPrice = productInfo[l]["shownPrice"]/100
    
                        tempProdDf = pd.DataFrame([{"productId":productId,
                                                    "productName":productName,
                                                    "regularPrice":regularPrice,
                                                    "loyaltyPrice":loyaltyPrice,
                                                    "salePrice":salePrice,
                                                    "shownPrice":shownPrice,
                                                    "categoryId":motherCategoryId,
                                                    "categoryName":motherCategoryName,
                                                    "subCategoryId":level1Id,
                                                    "subCategoryName":level1CatName,
                                                    "date":today}])            
                        
                        resultDf = resultDf.append(tempProdDf)
                        
    toc = time.perf_counter()
    print(f"Market scrapped in {toc - tic:0.4f} seconds")
    print(f"Market scrapped in {(toc - tic)/60:0.2f} minutes")
    
    return resultDf


def saveDataCSV(resultDf,localPath,fileName):
    '''
    saves dataframe to disk as csv

    Parameters
    ----------
    resultDf : Dataframe
        Dataframe that you want to save.
    localPath : str
        local path.
    fileName : str
        fileName.

    Returns
    -------
    None.

    '''
    today = datetime.date.today()
    resultDf.to_csv(localPath+(str(today)+fileName+".csv"))
    print('file {} is saved to {}'.format(fileName,localPath))
    

#%%