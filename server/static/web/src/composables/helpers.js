import { ref } from 'vue'

export function useFormatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-GB', {dateStyle: 'medium', timeStyle: 'short'}).format(date);
}

export function humanUnits(value){
    const units = ["k","M","G"]
    if (value < 1000) return Math.max(value)
    let i = -1;
    do {
      value = value / 1000;
      i++;
    } while (value >= 1000);
    return Math.max(value).toFixed(1) + units[i]
  }

export function round(value){
  return Math.round(value)
}

export function now(){
  return Math.round(Date.now()/1000)
}