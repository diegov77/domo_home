//TEMPERATURA
#include "DHT.h"
#define DHTPIN 13
#define DHTTYPE DHT11 
DHT dht(DHTPIN, DHTTYPE);
//LUZ
#define RELAY1  7 //lampara 1
#define RELAY2  6 //lampara 2
//SENSOR GAS
#define         MQ2                       (0)                   //define la entrada analogica para el sensor
#define         RL_VALOR             (5)                        //define el valor de la resistencia mde carga en kilo ohms
#define         RAL       (9.83)                                 // resistencia del sensor en el aire limpio / RO, que se deriva de la     tabla de la hoja de datos
#define         GAS_LP                      (0)
String pi_data;
const int PIRPin = 2;  
int alarmMovState = 0;
int alarmGasState = 0;
int pir_val = 0; 
//SENSOR GAS
String inputstring = "";                                           //Cadena recibida desde el PC
float           LPCurve[3]  =  {2.3,0.21,-0.47};
float           Ro           =  10; 
//CERRADURA
int lock = 9;  
        
void setup() {
  Serial.begin(9600);
  pinMode(lock,OUTPUT);
  pinMode(RELAY1,OUTPUT);
  pinMode(RELAY2,OUTPUT);
  digitalWrite(RELAY1,1); //LUZ DEFAULT OFF
  digitalWrite(RELAY2,1); //LUZ DEFAULT OFF
  digitalWrite(lock,  LOW);//CERRADURA
  //TEMPERATURA
  dht.begin();
  //SENSOR GAS
  Ro = Calibracion(MQ2);     //Calibrando el sensor
}

void loop() {
          
       
          if (Serial.available() ){
             //LECTURA DE SERIAL DEL RASPBERRY
        if (Serial.available()) {
              delay(3);
             // char c = Serial.read();
            //  pi_data += c; 
             pi_data = Serial.readString();
                }
             
               pi_data.trim();

               if(pi_data=="status"){
                 Serial.println("status ok");
                
               }
                    //LAMPARA 1
                if(pi_data == "LIGHT_ON_L1"){
                   Serial.print("Luz encendida");
                    digitalWrite(RELAY1,0); 
                   
                }else{
                   if(pi_data=="LIGHT_OFF_L1"){
                      Serial.print("Luz encendida");
                    digitalWrite(RELAY1,1); 
                   }
                }
                 //LAMPARA 2
                 if(pi_data == "LIGHT_ON_L2"){
                   Serial.print("Luz encendida");
                    digitalWrite(RELAY2,0); 
                   
                }else{
                   if(pi_data=="LIGHT_OFF_L2"){
                    digitalWrite(RELAY2,1); 
                   }
                   
                }

                    
    //ACTIVA Y DESACTIVA LA ALARMA
       if(pi_data.equals("ALARM_MOV_ON")){
              alarmMovState=1;
               Serial.println("ALARMA MOV ACTIVADA");
              
             }
        if(pi_data=="ALARM_MOV_OFF"){
                 alarmMovState=0;
                 Serial.println("ALARMA MOV DESACTIVADA");
                   
               }
          if(pi_data=="ALARM_GAS_ON"){
              alarmGasState=1;
               Serial.println("ALARMA GAS ACTIVADA");

             }
        if(pi_data=="ALARM_GAS_OFF"){
                 alarmGasState=0;
                   Serial.println("ALARMA GAS DESACTIVADA");
                   
               }
               
      //LECTURA DE TEMPERATURA
          if(pi_data=="TEMPERATURA"){
             //Serial.println("TEMP");
              int t= dht.readTemperature();//Lee la temperatura   
              Serial.println(t);
             
            
          }
          if(pi_data=="HUMEDAD"){
            int h = dht.readHumidity();// Lee la humedad
             Serial.println(h);
            
          }
      

          //CERRADURA
          if( pi_data == "LOCK"){
            Serial.println(pi_data);
            digitalWrite(lock, LOW); 
           
           }else{
            if( pi_data == "UNLOCK"){
               digitalWrite(lock, HIGH); 
             Serial.println(pi_data);
            }
             
           }

             pi_data="";
        }

        
  
       
    //SI LA ALARMA ESTA ACTIVADA HACE LOS CONTROLES DE SEGURIDAD
     if(alarmMovState== 1){

       //SENSOR DE MOVIMIENTO - ALARMA
       pir_val = digitalRead(PIRPin);
       if (pir_val == HIGH)
      {
        
          Serial.println("HAY MOVIMIENTO");
          alarmMovState= 0;
        }
     
      }
      
      if(alarmGasState==1){
         //LECTURA DE GAS Y HUMO
        if(porcentaje_gas(lecturaMQ(MQ2)/Ro,GAS_LP) > 100 ){
      
           Serial.println("FUGA_GAS");
          
           alarmGasState=0;
          
       }
      }


}//FIN LOOP


 //SENSOR GAS
 
float calc_res(int raw_adc)
{
  return ( ((float)RL_VALOR*(1023-raw_adc)/raw_adc));
}
 
float Calibracion(float mq_pin){
  int i;
  float val=0;
    for (i=0;i<50;i++) {                    //tomar múltiples muestras
    val += calc_res(analogRead(mq_pin));

  }
  val = val/50;                      //calcular el valor medio
  val = val/RAL;
  return val;
}
 
float lecturaMQ(int mq_pin){
  int i;
  float rs=0;
  for (i=0;i<5;i++) {
    rs += calc_res(analogRead(mq_pin));

  }
rs = rs/5;
return rs;
}
 
int porcentaje_gas(float rs_ro_ratio, int gas_id){
   if ( gas_id == GAS_LP ) {
     return porcentaje_gas(rs_ro_ratio,LPCurve);
   }
  return 0;
}
 
int porcentaje_gas(float rs_ro_ratio, float *pcurve){
  return (pow(10, (((log(rs_ro_ratio)-pcurve[1])/pcurve[2]) + pcurve[0])));
}
