import {
  useWatch,
  type FieldValues,
  type Path,
  type PathValue,
  type UseFormReturn,
} from "react-hook-form";
import { SugestaoIA } from "./SugestaoIA";

interface Props<T extends FieldValues> {
  form: UseFormReturn<T>;
  /** Campo de texto do formulário que recebe a sugestão. */
  campo: Path<T>;
  rotuloBloco: string;
  sugerir: (texto: string) => Promise<string>;
}

/** Liga um campo de texto do formulário ao botão "Sugestões de IA" (JOB-0034). */
export function SugestaoCampo<T extends FieldValues>({
  form,
  campo,
  rotuloBloco,
  sugerir,
}: Props<T>) {
  const texto = useWatch({ control: form.control, name: campo });
  return (
    <SugestaoIA
      rotuloBloco={rotuloBloco}
      textoAtual={String(texto ?? "")}
      sugerir={sugerir}
      aplicar={(sugestao) =>
        form.setValue(campo, sugestao as PathValue<T, Path<T>>, {
          shouldDirty: true,
          shouldTouch: true,
        })
      }
      focarCampo={() => form.setFocus(campo)}
    />
  );
}
