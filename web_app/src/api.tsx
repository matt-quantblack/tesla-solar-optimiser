import axios, {CancelToken, Method} from "axios";
import {keysToCamel, keysToSnake} from "./hooks/NamingConverter";

const api_version = "v1";
const base_url = `${process.env.REACT_APP_HOST}/api/${api_version}`

function axiosHelper (
    url: string,
    cancelToken?: CancelToken,
    method: Method='GET',
    data: any=null,
    contentType: string='application/json') {

    let config: {[key: string]: any} = {
        "url": url,
        "method": method,
        "headers": {
            "content-type": contentType
        },
        // convert keys to snake case for python backend if this is json data
        "data": contentType === 'application/json' ? keysToSnake(data) : data
    };

    if (cancelToken !== undefined)
        config = {...config, "cancelToken": cancelToken}

    return axios(config)
      .then((response: any) => {
        const json = keysToCamel(response.data);
        return json;
      });
}

// Get the current charging state
const getSolarChargeState = () => axiosHelper(`${base_url}/solar_charge_state`);

const api = {
    getSolarChargeState: getSolarChargeState};
export default api;