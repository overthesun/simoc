<!-- component used for the holding the login / registration components. See EntryView for further details-->

<template>
    <div class='entry-wrapper'>
        <header class='header'>
            <img src='../../assets/simoc-logo.svg' class='simoc-logo'/>
            <span class='simoc-logo-title'>SIMOC</span>
        </header>
        <div class='main-options'>
            <slot name="option-items"></slot>
        </div>
        <main class='main'>
            <slot name='entry-main'></slot>           
        </main>
        <div class='entry-button-wrapper'>
            <slot name='entry-button'></slot>
        </div>
        <footer class='footer'>
            <slot name='entry-footer'></slot>
        </footer>
    </div>
</template>

<script>
export default {

}
</script>

<style lang="scss" scoped>
    .entry-wrapper{
        height:100%;
        width:100%;
        display:flex;
        justify-content:center;
        align-items:center;
        flex-direction:column;
        box-sizing:border-box;
        position:relative;
    }

    .warning-wrapper{
        position:absolute;
        left:0;
        top:-256px;
        z-index:99;
        height: auto;
        min-height:128px;
        max-height:256px;
        width:100%;
        background-color:#ff3100;
        transition: top .5s ease;
        padding:16px;
        box-sizing:border-box;
        border-bottom: 1px solid #eee;
        display:flex;
        justify-content:center;
        align-items:center;
        flex-direction:column;
        color:white;

        .dismiss-icon{
            position:absolute;
            top:0;
            right:0;
            margin:4px 8px;
            padding:4px;

            &:hover{
                cursor: pointer;
            }
        }
    }

    .warning-active{
        top:0px;
    }
    
    .header{
        display:flex;
        justify-content:center;
        align-items:center;
        margin-bottom: 32px;
    }

    .simoc-logo{
        width: auto;
        height: 48px;
        margin-right:8px;
    }

    .simoc-logo-title{
        font-weight: 400;
        font-size: 22px;
    }

    .main-options{
        display:flex;
        justify-content:center;
        align-items:center;
        margin-bottom: 48px;
    }

    .option-item{
        box-sizing:border-box;
        margin: 0px 16px; 
        font-weight: 600;
        font-size: 24px;
        position: relative;

        &:hover{
            cursor:pointer;
        }

        &:after{
            box-sizing:border-box;
            position: absolute;
            right: 0;
            top: 100%;
            content:"";
            width: 0;
            border-bottom: 2px solid lightgreen;
            transition: width .2s ease;
        }

        &-active:after{
            width: 100%;
            left:0;
        }
    }

    .main{        
        box-sizing:border-box;
        width:100%;
        height:100%;
        max-height:100%;
        display:flex;
        justify-content:flex-start;
        align-items:center;
        flex-direction:column;
        margin-bottom:48px;
        overflow: hidden;
        overflow-y:auto;
        position:relative;
    }


    .link{
        text-decoration: underline;
        &:visited,&{
            color:lightgreen;
        }

        &-disabled{
            color: #999;
        }
    }

    .entry-button-wrapper{
        width:100%;
        height:48px;
        min-height:48px;
        margin-bottom: 32px;
        position:relative;
        display:flex;
        justify-content:center;
        align-items:center;
    }

    .btn-normal{
        width: 256px;
        height: 48px;
        min-height: 48px;
        margin-bottom: 24px;
        border-radius: 24px;
        padding: 12px 16px;
        font-size: 16px;
        font-weight: 600;
        background-color: #0099ee;
        border:none;
        color: #eee;

        &:hover{
            cursor: pointer;
        }

        &:focus{
            outline:none;
        }
    }

    .btn-warning{
        margin-top:auto;
        width: 256px;
        height: 48px;
        min-height:48px;
        margin-top: auto;
        border-radius: 24px; 
        padding: 12px 16px;
        font-size: 16px;
        font-weight: 600;
        background-color: #0099ee;
        border:none;
        //border: 2px solid #eee;
        color: #eee;

        &:hover{
            color: #eee;
            cursor: pointer;
        }

        &:focus{
            outline:none;
        }
    }

    .btn-disabled{
        background-color: #4c4c4c;
        color: #999;
    }

    .footer{
        width: 100%;
        height: 24px;
        min-height:24px;
        display:flex;
        justify-content:space-around;
        align-items:center;
    }
</style>
