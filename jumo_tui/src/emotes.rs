const NEUTRAL_SMILE: &str = r"

▟█▙             ▟█▙
▜█▛             ▜█▛

       ▚▄▄▄▞       
";

const SMIELY: &str = r"

▟█▙             ▟█▙
▜█▛             ▜█▛

       ▜███▛       
";

const HAPPY: &str = r"


▞▀▀▚           ▞▀▀▚

       ▚▄▄▄▞       
";

const SUNGLASSES: &str = r"


▜█████▛▀▀▀▀▀▜█████▛
 ▜███▛       ▜███▛
       ▚▄▄▄▞       
";

const WINK: &str = r"

▟█▙                
▜█▛           ▀▀▀▀▀

       ▚▄▄▄▞       
";

const NEUTRAL: &str = r"

▟█▙             ▟█▙
▜█▛             ▜█▛

       ▄▄▄▄▄       
";

const EXPRESSIONLESS: &str = r"


▀▀▀▀           ▀▀▀▀

       ▄▄▄▄▄       
";

const SMILE: &str = r"


▞▀▀▚           ▞▀▀▚

       ▜███▛       
";

const SWEAT_SMILE: &str = r"

                         ▟▙
    ▞▀▀▚           ▞▀▀▚  ▀▀

           ▜███▛           
";

const UPSIDE_DOWN: &str = r"

       ▞▀▀▀▚       

▟█▙             ▟█▙
▜█▛             ▜█▛
";

const THINKING: &str = r"
▞▀▀▀▀▚              
                    
 ▀▀▀▀           ▀▀▀▀

        ▄▄▄▄▄       
";

const CURIOUS: &str = r"
▞▀▀▀▀▚         ▞▀▀▀▀▚
                  
 ▀▀▀▀           ▀▀▀▀

        ▄▄▄▄▄       
";

const CONCERNED: &str = r"

▟█▙             ▟█▙
▜█▛             ▜█▛

       ▞▀▀▀▚       
";

pub fn get_emote(emote: &str) -> &str {
    match emote {
        "NEUTRAL_SMILE" => NEUTRAL_SMILE,
        "SMILEY" => SMIELY,
        "HAPPY" => HAPPY,
        "SUNGLASSES" => SUNGLASSES,
        "WINK" => WINK,
        "NEUTRAL" => NEUTRAL,
        "EXPRESSIONLESS" => EXPRESSIONLESS,
        "THINKING" => THINKING,
        "SMILE" => SMILE,
        // TODO: maybe make a unique one for this
        "EXCITED" => SMILE,
        "SWEAT_SMILE" => SWEAT_SMILE,
        "UPSIDE_DOWN" => UPSIDE_DOWN,
        "CURIOUS" => CURIOUS,
        "CONCERNED" => CONCERNED,
        _ => "???",
    }
}
