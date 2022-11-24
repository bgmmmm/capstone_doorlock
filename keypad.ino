//keypad.ino ->키패드 동작 모듈

#include <Wire.h>
#include <EEPROM.h>
#include <string.h>
#include <SoftwareSerial.h>
#include "Adafruit_MPR121.h"

#ifndef _BV
#define _BV(bit) (1 << (bit)) 
#endif

Adafruit_MPR121 cap = Adafruit_MPR121();
SoftwareSerial hc06(2,3);

uint16_t lasttouched = 0;
uint16_t currtouched = 0;
int pressed=0;

char keymap[12]={'1','4','7','*','2','5','8','0','3','6','9','#'}; //입력값 매핑
char passWD[7]={'\0','\0','\0','\0','\0','\0','\0'}; //비밀번호, EEPROM에서 읽어올 예정

int errstack=0; //비밀번호 틀린 횟수 저장

char buffA[7]; // 입력값 저장
char buffB[7]; // 재입력 입력값 저장

void setup()
{
  Serial.begin(9600); //시리얼 통신 연결
  hc06.begin(9600); //HC06 연결
  pinMode(8,OUTPUT); //부저 핀 설정
  cap.begin(0x5A); //키패드 연결
  int i=0;
  while(i<7) //EPROM에서 휘발성 메모리인 passWD로 비밀번호를 받아들임
  {
    passWD[i]=EEPROM.read(i);
    if(passWD[i]=='\0')
      break;
    i++;
  }
}

void buzzer_input() //부저 울리는 함수: 버튼 누를 때
{
  tone(8,2489,100);
  delay(300);
}

void buzzer_error() //부저 울리는 함수: 에러음
{
    tone(8,1046,250);
    delay(300);
    tone(8,1046,150);
    delay(500);
   return;
}

void buzzer_ok() //부저 울리는 함수: OK음
{
   tone(8,2793,250);
   delay(280);
   tone(8,3520,250);
   delay(280);
   tone(8,4186,200);
   delay(500);
   return;
}

void buzzer_check() //부저 울리는 함수: 체크음(다시 한 번 입력하세요)
{
   tone(8,2793,250);
   delay(280);
   tone(8,3520,180);
   delay(300);
   return;
}

void buzzer_lock() //부저 울리는 함수: 잠금음
{
   tone(8,2793,250);
   delay(280);
   tone(8,3520,180);
   delay(300);
   return;
}

int inputkey(char buff[]) //키패드 입력
{
  int cnt=0;
  while(1)
  {
     currtouched = cap.touched();
     for (uint8_t i=0; i<12; i++)
      {
        if ((currtouched & _BV(i)) && !(lasttouched & _BV(i)) ) //오작동 대비 빈칸으로 남겨둠
        {
          ;
        }
        if (!(currtouched & _BV(i)) && (lasttouched & _BV(i)) ) //키가 눌렸다가 떼졌을 때의 조건
        {
          if(keymap[i]=='#') //# 버튼을 누르면 #는 입력 배열에 저장하지 않고 터치값 초기화, 입력 함수 종료
          {
           buzzer_input();
           lasttouched = currtouched;
           for(int j=cnt;j<7;j++)
              buff[j]='\0';
           return cnt;
          }
           buff[cnt]=keymap[i]; //#가 아닐 경우 keymap에서 해당하는 값을 찾아 입력 배열에 저장, 부저 울림
           cnt++;
           buzzer_input();
        }
       }
     lasttouched = currtouched; //터치 값 초기화
      
     if (cnt>6 && buff[6]!='#') //'#' 빼고 입력이 6자리를 초과했을 경우 입력 함수 강제 종료
      {
        errstack+=1;
        return cnt;
      }
   }
} 

void newpasswd() //새로운 비밀번호 설정 함수
{
  buzzer_check(); //체크음을 울리고, 기존 비밀번호를 입력한다
  inputkey(buffA);
    
  if(strcmp(passWD,buffA)==0) //기존 비밀번호 체크를 통과했을 경우
  {
    buzzer_ok(); //OK음 출력하고 새로운 비밀번호를 입력한다
    delay(500);
    buzzer_check();
    memset(buffA,'\0',sizeof(buffA)/sizeof(char));
    memset(buffB,'\0',sizeof(buffB)/sizeof(char));
    int cnt=inputkey(buffA);
    
    if(cnt>=4&&cnt<=6) //새 비밀번호가 비밀번호 길이 조건에 맞을 경우
    {
      buzzer_check();
      inputkey(buffB);     
      if(strcmp(buffB,buffA)==0) //두 입력이 맞으면 OK음 출력, 비밀번호 변경 후 비밀번호 변경 함수 종료
      {
        strcpy(passWD,buffA);
        for(int i=0;i<cnt;i++)
        {
          char c=buffA[i];
          EEPROM.write(i,c);
        }
        for(int i=cnt;i<7;i++)
        {
          EEPROM.write(i,'\0');
        }
        buzzer_ok();
        memset(buffA,'\0',sizeof(buffA)/sizeof(char));
        memset(buffB,'\0',sizeof(buffB)/sizeof(char));
        return;
      }
      else //두 입력이 틀리면 에러음 출력, 비밀번호 변경 함수 종료
      {
        memset(buffA,'\0',sizeof(buffA)/sizeof(char));
        memset(buffB,'\0',sizeof(buffB)/sizeof(char));
        buzzer_error();
        return;
      }
    }
    else if(cnt<4) //비밀번호가 너무 짧은 경우 , 에러음을 출력하고 비밀번호 변경 함수 종료
    {
      memset(buffA,'\0',sizeof(buffA)/sizeof(char));
      memset(buffB,'\0',sizeof(buffB)/sizeof(char));
      buzzer_error();
      return;
    }
    else if(cnt>6) //비밀번호가 너무 긴 경우, (에러음은 inputkey에서 이미 출력했음) 비밀번호 변경 함수 종료
    {
      memset(buffA,'\0',sizeof(buffA)/sizeof(char));
      memset(buffB,'\0',sizeof(buffB)/sizeof(char));
      return;
    }
  }
  else //기존 비밀번호 체크를 미통과했을 경우, 에러음을 출력하고 완전 종료
  {
    memset(buffA,'\0',sizeof(buffA)/sizeof(char));
    buzzer_error();
    return;
  }
}

void loop()
{
  inputkey(buffA);
  if(strcmp(buffA,"*1*1*")==0) // 비밀번호 변경 함수 호출조건. 라즈베리파이에 보내는 값 없음
  {
    memset(buffA,'\0',sizeof(buffA)/sizeof(char));
    newpasswd();
    return 0;
  }
  else if(strcmp(buffA,"*4*4*")==0) // 새로운 얼굴 촬영 호출조건. 라즈베리파이에 보내는 값 4
  {
    memset(buffA,'\0',sizeof(buffA)/sizeof(char));
    buzzer_check(); //체크음을 울리고, 비밀번호를 입력한다
    inputkey(buffA);
    if(strcmp(passWD,buffA)==0) // 비밀번호 입력시 뭔가 일어남(새 얼굴 촬영)
    {
      buzzer_ok(); //OK음 출력하고 비밀번호를 다시 입력한다.
      memset(buffA,'\0',sizeof(buffA)/sizeof(char));
      memset(buffB,'\0',sizeof(buffB)/sizeof(char));
      hc06.write("2");
      return 2;
    }
    else
    {
      memset(buffA,'\0',sizeof(buffA)/sizeof(char));
      memset(buffB,'\0',sizeof(buffB)/sizeof(char));
      buzzer_error();
      return 0;
    }
  }
  else if(strcmp(buffA,"*7*7*")==0) // 얼굴 전부 초기화 호출조건. 라즈베리파이에 보내는 값 7
  {
    memset(buffA,'\0',sizeof(buffA)/sizeof(char));
    buzzer_check(); //체크음을 울리고, 비밀번호를 입력한다
    inputkey(buffA);
    if(strcmp(passWD,buffA)==0) // 비밀번호 입력시 뭔가 일어남(얼굴 초기화)
    {
      buzzer_ok(); //OK음 출력하고 비밀번호를 다시 입력한다.
      memset(buffA,'\0',sizeof(buffA)/sizeof(char));
      memset(buffB,'\0',sizeof(buffB)/sizeof(char));
      hc06.write("3");
      return 3;
    }
    else
    {
      memset(buffA,'\0',sizeof(buffA)/sizeof(char));
      memset(buffB,'\0',sizeof(buffB)/sizeof(char));
      buzzer_error();
      return 0;
    }
  }
  else
  {
    if(strcmp(passWD,buffA)==0) //비밀번호가 맞았을 경우. 라즈베리파이에 보내는 값은 1
    {
      buzzer_ok();
      hc06.write("1");
      errstack=0;
      return 1;
    }
    else //비밀번호가 틀렸을 경우. 에러음 출력하고 문이 안 열림. 라즈베리파이에 보내는 값 없음
    {
      buzzer_error();
      errstack+=1;
      if( errstack>=3 ) //비밀번호 3회 이상 틀렸을 시 3분간 도어락 잠금
      {
        buzzer_error();
        delay(180000);
        errstack=0
				buzzer_lock();
      }
      return 0;
    }
  }
}