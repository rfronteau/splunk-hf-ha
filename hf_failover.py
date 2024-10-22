import splunk.Intersplunk
import sys
import requests
import json

def manage_splunk_input(splunk_host, splunk_port, splunk_user, splunk_password, user, inputs, action):
    """Enables or disables a Splunk input."""

    results = {}
    session = requests.Session()

    for input_name in inputs:
        url = f"https://{splunk_host}:{splunk_port}/servicesNS/{user}/{input_name}"

        if action =="enable":
            url += "/enable"
        elif action == "disable":
            url += "/disable"
        else:
            raise ValueError("Invalid action. Use 'enable' or 'disable'.")

        try:
            response = session.post(url, auth=(splunk_user, splunk_password), verify=False)  # Adjust verify=False if needed for self-signed certificates

            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            results[input_name] = {"status_code": response.status_code, "response": response.text}

        except requests.exceptions.RequestException as e:
            results[input_name] = {"status_code": e.response.status_code if hasattr(e, "response") else -1, "response": str(e)} # Store error information

    session.close() # Close the session
    return results


try:
        splunk_host = "localhost"
        splunk_port = 8089
        username = "admin"
        password = "xxxxxxxxxxxx"
        splunk_user = "nobody"
        inputs_to_manage = [
                "Splunk_TA_AppDynamics/data/inputs/appdynamics_summary/cov_appdyn_prod_input_summary",
                "Splunk_TA_vmware_inframon/data/inputs/script/%24SPLUNK_HOME%252Fetc%252Fapps%252FSplunk_TA_vmware_inframon%252Fbin%252Fta_vmware_hierarchy_agent.py",
                "Splunk_TA_vmware_inframon/data/inputs/ta_vmware_collection_scheduler_inframon/Global%20pool"
        ]
        splunk_app = "Splunk_TA_AppDynamics"
        input_type = "appdynamics_summary"
        input_name = "cov_appdyn_prod_input_summary"

        # Access the previous search results (replace with actual method)
        results, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()

        # Example: Iterate through the previous results and extract relevant fields
        for result in results:
                is_not_me = result['is_not_me']
                splunk_hf = result['host']
                splunk_role = result['role']
                hf_state = result['state']
                pass_active = result['need_active']
                pass_passive = result['need_passive']

                switch_pointer = result['need_to_switch']
                print('need to switch', switch_pointer)

                if is_not_me == '1':
                        splunk_host = result['host']
                else:
                        splunk_host = "localhost"

                if switch_pointer == '1':
                        print("It's time to switch pointer is to %s", switch_pointer)
                        manage_splunk_input(splunk_host, splunk_port, username, password, splunk_user, inputs_to_manage, "enable")
                if pass_passive == '1':
                        print(splunk_hf, " need to become passive")
                        manage_splunk_input(splunk_host, splunk_port, username, password, splunk_user, inputs_to_manage, "disable")
                if pass_active == '1':
                        print(splunk_hf, " need to become active")
                        manage_splunk_input(splunk_host, splunk_port, username, password, splunk_user, inputs_to_manage, "enable")

        # Output the processed results
        splunk.Intersplunk.outputResults(results)

except Exception as e:
        # Handle exceptions (log, retry, return error, etc.)
        splunk.Intersplunk.generateErrorResults(str(e))



