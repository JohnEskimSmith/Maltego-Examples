from maltego_trx.entities import GPS, Image, URL
from requests import post as send_post
from maltego_trx.transform import DiscoverableTransform
from maltego_trx.maltego import UIM_TYPES
import logging

# my service
# POST json like {"places": ["UN NY", "Moscow"]}
# POST json like {"places": ["address1", "address2", "Company Name"]}
host, port = "68.183.0.119", "8080"

template_url ="http://{host}:{port}/tasks/proxy/places"
class SearchPlaces(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request, response):
        logger = logging.getLogger('project')
        try:
            input_data = [request.Value]
            try:
                input_data_json = {"places": input_data}

                url = template_url.format(host=host, port=port)
                resource = send_post(url, json=input_data_json)
            except Exception as e:
                response.addUIMessage("Error: " + str(e), UIM_TYPES["partial"])
            else:
                if resource.status_code == 200:
                    output_data = resource.json()
                    if output_data['status']:
                        for block in output_data['result']:
                            for line in block["rows"]:
                                logger.info(line)
                                lat, lon = round(line['lat'], 5), round(line['lon'], 5)
                                _record_str = f"{lat},{lon}"
                                en = response.addEntity(GPS, _record_str)
                                en.addProperty(displayName="latitude", fieldName="latitude", value=lat)
                                en.addProperty(displayName="longitude", fieldName="longitude", value=lon)
                                if 'link_to_image' in line:
                                    if len(line['link_to_image']) > 0:
                                        en = response.addEntity(Image, line['name_address'])
                                        en.addProperty(displayName="description", fieldName="description", value=line['name_address'])
                                        en.addProperty(displayName="url", fieldName="url", value=line['link_to_image'])
                                if 'link_to_plus_codes' in line:
                                    if len(line['link_to_plus_codes']) > 0:
                                        link_to_codes = line['link_to_plus_codes']
                                        en = response.addEntity(URL, link_to_codes)
                                        en.setLinkLabel('Google plus codes')
                                        en.addProperty(displayName="url", fieldName="url", value=line['link_to_plus_codes'])
                                        en.addProperty(displayName="title", fieldName="title",
                                                       value="Location with Google plus codes")
                                        _google_address = str(line["formatted_address"]).encode('utf-8')
                                        # sorry, dev with Windows 10 with local RU
                                        google_address = _google_address.decode('cp1251')
                                        en.addDisplayInformation(f'<a href="{line["link_to_plus_codes"]}">{google_address}</a>', "Map with Google")

        except Exception as e:
            response.addUIMessage("Error: " + str(e), UIM_TYPES["partial"])
