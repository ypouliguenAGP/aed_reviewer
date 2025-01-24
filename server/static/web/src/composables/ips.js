import { ref } from 'vue'

export function useSimplePrefixe(prefix){
    if (prefix.split('/')[1] == '32') return ' '+prefix.split('/')[0]
    return ' '+prefix
}
