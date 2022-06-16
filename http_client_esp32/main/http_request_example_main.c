/* HTTP GET Example using plain POSIX sockets

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "protocol_examples_common.h"

#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include "lwip/netdb.h"
#include "lwip/dns.h"

/*
    TAREFAS SEGUINTES

    - Implementar 2 var globais, uma já tem (read_event) e a outra é para atualizar em caso de respostas que não são eventos (different, finished, stopped...)
    se não perde-se a atualização da lista do servidor com um evento não controlável
    - Continuar a Implementação da máquina de estados (Rafael p explicar oq cada um significa)
    - Finalizar a lógica (LEDs).

*/

/* Constants that aren't configurable in menuconfig */
#define WEB_SERVER "192.168.0.71"
#define WEB_PORT "8000"

static const char *TAG = "example";
char event_read[30] = "";
char event_to_update[30] = "";
int event_to_process = -1;
char request2[25] = "PUT /confirm_event?event=";

/* State machine representation:
    0 - waiting for an event
    1 - will update an event
*/
int state_machine = 0;
int processed = 0;

static const char *request1 = "GET " "/get_event" " HTTP/1.0\r\n"
    "Host: "WEB_SERVER":"WEB_PORT"\r\n"
    "User-Agent: esp-idf/1.0 esp32\r\n"
    "\r\n";

static const char *req_patter = " HTTP/1.0\r\n"
            "Host: "WEB_SERVER":"WEB_PORT"\r\n"
            "User-Agent: esp-idf/1.0 esp32\r\n"
            "\r\n";

static int socket_connection(){
    const struct addrinfo hints = {
        .ai_family = AF_INET,
        .ai_socktype = SOCK_STREAM,
    };
    struct addrinfo *res;
    struct in_addr *addr;
    int s;

    int err = getaddrinfo(WEB_SERVER, WEB_PORT, &hints, &res);

    if(err != 0 || res == NULL) {
        ESP_LOGE(TAG, "DNS lookup failed err=%d res=%p", err, res);
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }

    /* Code to print the resolved IP.

        Note: inet_ntoa is non-reentrant, look at ipaddr_ntoa_r for "real" code */
    addr = &((struct sockaddr_in *)res->ai_addr)->sin_addr;
    //ESP_LOGI(TAG, "DNS lookup succeeded. IP=%s", inet_ntoa(*addr));

    s = socket(res->ai_family, res->ai_socktype, 0);
    if(s < 0) {
        ESP_LOGE(TAG, "... Failed to allocate socket.");
        freeaddrinfo(res);
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
    //ESP_LOGI(TAG, "... allocated socket");

    if(connect(s, res->ai_addr, res->ai_addrlen) != 0) {
        ESP_LOGE(TAG, "... socket connect failed errno=%d", errno);
        close(s);
        freeaddrinfo(res);
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }

    ESP_LOGI(TAG, "... connected");
    freeaddrinfo(res);

    return(s);
}

static void set_timeout(int s){
    struct timeval receiving_timeout;
    receiving_timeout.tv_sec = 5;
    receiving_timeout.tv_usec = 0;
    if (setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, &receiving_timeout,
            sizeof(receiving_timeout)) < 0) {
        ESP_LOGE(TAG, "... failed to set socket receiving timeout");
        close(s);
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
}

static void readHttpResponse(int s){

    char recv_buf[64];
    int r;
    char a;
    int cont_num_characters = 0;
    int firt_json_element = 0;

    memset(event_read,0,sizeof(event_read));

    do {
            bzero(recv_buf, sizeof(recv_buf)); //zera a região de memória para gravar uma nova mensagem
            r = read(s, recv_buf, sizeof(recv_buf)-1); // r é o número de bytes lido
            for(int i = 0; i < r; i++) {
                if( recv_buf[i] > 31){
                    a = (char)recv_buf[i];
                    if( a == '{' ){
                        firt_json_element = cont_num_characters;
                    }
                    if( (firt_json_element > 0) && (cont_num_characters > (firt_json_element + 11)) && (a != '"') && (a !='}') ){ // Já encontrou o caracter '{'
                        strncat(event_read, &a , 1);
                    }
                }
                cont_num_characters += 1;
            }
            
    } while(r > 0);
    printf("\n------ Chegou aqui, evento: %s \n", event_read);
    
}

static void stateMachineControl(){

    if(strcmp(event_read, "B1_SOURCE") == 0){

        // CONFIRM EVENT GOT
        ESP_LOGI(TAG, "The event will be confirmed!");
        strcpy(event_to_update, "B1_SOURCE");
        state_machine = 1;
        event_to_process = 1;
        processed = 0;

    }else if(strcmp(event_read, "B1_PREPARATION_LINE_A") == 0){

        state_machine = 1;
        event_to_process = 2;
    }else if(strcmp(event_read, "B1_PREPARATION_LINE_B") == 0){
        
        event_to_process = 3;
    }else if(strcmp(event_read, "B1_LINE_A") == 0){
 
        // EXECUTE SOME MOVIMENTS

        // START NON-MODELED EVENTS
        int sequence_triggered = 0; // Sequence to be triggered that is not modeled

        // nonModeledEvents(sequence_triggered);

        // SEND THE END'S EVENT UNCONTROLLABLE

    }else if(strcmp(event_read, "B1_LINE_B") == 0){
        

    }else if(strcmp(event_read, "B1_POINT_OF_INTEREST_A") == 0){
        

    }else if(strcmp(event_read, "B1_POINT_OF_INTEREST_B") == 0){
        

    }else if(strcmp(event_read, "B1_SOURCE_A") == 0){
        

    }else if(strcmp(event_read, "B1_SOURCE_B") == 0){
        

    }else if(strcmp(event_read, "B1_STOP") == 0){
        

    }else if(strcmp(event_read, "B1_SUPPORT") == 0){
        

    }else if(strcmp(event_read, "B1_MAINTENANCE") == 0){
        

    
    }else if(strcmp(event_read, "stopped") == 0){ // state_machine is 0 always that the return is 'stopped'
        ESP_LOGI(TAG, "Production has not started, after 3 seconds a event will be get again!");
        vTaskDelay(3000 / portTICK_PERIOD_MS);
        
    }else if(strcmp(event_read, "finished") == 0){ // state_machine is 0 or 2, because finished can be received from get_event or confirm_event routes
        ESP_LOGI(TAG, "Production has finished, after 3 seconds a event will be get again!");
        vTaskDelay(3000 / portTICK_PERIOD_MS);
        state_machine = 0;

    }else if(strcmp(event_read, "updated") == 0){
        ESP_LOGI(TAG, "Production has updated, an new event will be get again!");
        if(state_machine == 1){
            state_machine = 2;
        }else{
            state_machine = 0;
        }

    }else if(strcmp(event_read, "different") == 0){ // event_read == 'different', state_machine is 1
        ESP_LOGI(TAG, "Event to be updated is different that the server is waiting, so will be send again!");
        vTaskDelay(1000 / portTICK_PERIOD_MS);

    }else{
        ESP_LOGI(TAG, "Server is down, waiting to be up!");
        vTaskDelay(5000 / portTICK_PERIOD_MS);
    }
}

static void stateMachineWork(){

    switch(event_to_process){

        case 1: // B1_SOURCE
            // EXECUTE SOME MOVIMENTS AND SEND AN EVENT
            ESP_LOGI(TAG, "Event B1_SOURCE is processing!");
            vTaskDelay(5000 / portTICK_PERIOD_MS);

            // SEND THE EVENT OF END THAT IS UNCONTROLLABLE
            strcpy(event_to_update, "B1_SOURCE_END");
            processed = 1;

        break; 

        case 2: // B1_PREPARATION_LINE_A

        break;

        case 3: // B1_PREPARATION_LINE_B

        break;

        case 4: // B1_LINE_A

        break;

        case 5: // B1_LINE_B

        break;

        case 6: // B1_POINT_OF_INTEREST_A

        break;

        case 7: // B1_POINT_OF_INTEREST_B

        break;

        case 8: // B1_SOURCE_A

        break;

        case 9: // B1_SOURCE_B

        break;

        case 10: // B1_STOP

        break;

        case 11: // B1_SUPPORT

        break;

        case 12: // B1_MAINTENANCE

        break;
    }
}

// static void nonModeledEvents(int sequence){

//     if(sequence == 0){
//         ESP_LOGI(TAG, "Executing sequence 0 with 1 events!");
//         vTaskDelay(2000 / portTICK_PERIOD_MS);
//     }else{
//         ESP_LOGI(TAG, "Executing sequence 1 with 3 events!");
//         vTaskDelay(6000 / portTICK_PERIOD_MS);
//     }

// }

static void http_get_task(void *pvParameters)
{
    // Start the App logic
    while(1) {

        int s = socket_connection();

        // Robotic arm is waiting for an event
        if(state_machine == 0){

            // Send a request to get an event
            if (write(s, request1, strlen(request1)) < 0) {
                ESP_LOGE(TAG, "... socket send failed");
                close(s);
                vTaskDelay(1000 / portTICK_PERIOD_MS);
                continue;
            }

            set_timeout(s);
            readHttpResponse(s); // event_read will be updated
            stateMachineControl(); // State machine will work

        }else if(state_machine == 1){ // Confirm controllable events

            char aux[200] = "";
            strcat(aux, request2);
            strcat(aux, event_to_update);
            strcat(aux, req_patter);

            // Send a request to update an event
            if (write(s, aux, strlen(aux)) < 0) {
                ESP_LOGE(TAG, "... socket send failed");
                close(s);
                vTaskDelay(1000 / portTICK_PERIOD_MS);
                continue;
            }

            set_timeout(s);
            readHttpResponse(s); // event_read will be updated
            stateMachineControl();

        }else{ // will process and update an uncontrollable event

            if(processed == 0){
                stateMachineWork();
            }
            

            char aux[200] = "";
            strcat(aux, request2);
            strcat(aux, event_to_update);
            strcat(aux, req_patter);

            // Send a request to update an event
            if (write(s, aux, strlen(aux)) < 0) {
                ESP_LOGE(TAG, "... socket send failed");
                close(s);
                vTaskDelay(1000 / portTICK_PERIOD_MS);
                continue;
            }

            set_timeout(s);
            readHttpResponse(s); // event_read will be updated
            stateMachineControl();

        }

        close(s);

        for(int countdown = 1; countdown > 0; countdown--) {
            ESP_LOGI(TAG, "%d... ", countdown);
            vTaskDelay(500 / portTICK_PERIOD_MS);
        }
        ESP_LOGI(TAG, "Starting again!");
    }
}

void app_main(void)
{
    ESP_ERROR_CHECK( nvs_flash_init() );
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    /* This helper function configures Wi-Fi or Ethernet, as selected in menuconfig.
     * Read "Establishing Wi-Fi or Ethernet Connection" section in
     * examples/protocols/README.md for more information about this function.
     */
    ESP_ERROR_CHECK(example_connect());

    xTaskCreate(&http_get_task, "http_get_task", 4096, NULL, 5, NULL);
}