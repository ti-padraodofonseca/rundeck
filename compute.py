import oci
import time

resource_name = 'compute instances'

def start_compute_instances(config, signer, compartments):
    target_resources = []

    print("Listando todas {}... (Instâncias marcadas com * serão iniciadas)".format(resource_name))
    for compartment in compartments:
        # print("  compartment: {}".format(compartment.name))
        resources = _get_resource_list(config, signer, compartment.id)
        for resource in resources:
            go = 0
            if (resource.lifecycle_state == 'STOPPED'):
                if(time.strftime('%A', time.localtime()) == 'Saturday' or time.strftime('%A', time.localtime()) == 'Sunday'):
                    if ('rotinas' in resource.defined_tags) and ('liga-fds' in resource.defined_tags['rotinas']): 
                        if (resource.defined_tags['rotinas']['liga-fds'].split(':')[0] == time.strftime('%H', time.localtime())):
                            go = 1
                if(time.strftime('%A', time.localtime()) == 'Saturday'):
                    if ('rotinas' in resource.defined_tags) and ('liga-sabado' in resource.defined_tags['rotinas']): 
                        if (resource.defined_tags['rotinas']['liga-sabado'].split(':')[0] == time.strftime('%H', time.localtime())):
                            go = 1
                if(time.strftime('%A', time.localtime()) == 'Sunday'):
                    if ('rotinas' in resource.defined_tags) and ('liga-domingo' in resource.defined_tags['rotinas']): 
                        if (resource.defined_tags['rotinas']['liga-domingo'].split(':')[0] == time.strftime('%H', time.localtime())):
                            go = 1
                else:
                    if ('rotinas' in resource.defined_tags) and ('liga' in resource.defined_tags['rotinas']): 
                        if (resource.defined_tags['rotinas']['liga'].split(':')[0] == time.strftime('%H', time.localtime())):
                            go = 1           
            if (go == 1):
                print("    * {} ({}) em {}".format(resource.display_name, resource.lifecycle_state, compartment.name))
                target_resources.append(resource)
            else:
                print("      {} ({}) em {}".format(resource.display_name, resource.lifecycle_state, compartment.name))

    print('\nIniciando {} marcadas com *'.format(resource_name))
    for resource in target_resources:
        try:
           response = _resource_action(config, signer, resource.id, 'START')
        except oci.exceptions.ServiceError as e:
            print("---------> error. status: {}".format(e))
            pass
        else:
            if response.lifecycle_state == 'STARTING':
                print("    Inicio solicitado: {} ({})".format(response.display_name, response.lifecycle_state))
            elif response.lifecycle_state == 'STOPPED':
                print("    Inicando {} ({})".format(response.display_name, response.lifecycle_state))
            else:
                print("---------> erro iniciando {} ({})".format(response.display_name, response.lifecycle_state))

    print("\nTodas {} iniciadas!".format(resource_name))


def _get_resource_list(config, signer, compartment_id):
    object = oci.core.ComputeClient(config=config, signer=signer)
    resources = oci.pagination.list_call_get_all_results(
        object.list_instances,
        compartment_id
    )
    return resources.data

def _resource_action(config, signer, resource_id, action):
    object = oci.core.ComputeClient(config=config, signer=signer)
    response = object.instance_action(
        resource_id,
        action
    )
    return response.data
